"""
Product Knowledge Agent for Security Products

This agent provides detailed product knowledge for security products (Prisma Cloud and Carbon Black)
by retrieving and indexing documentation and answering product-specific questions.
"""

import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import anthropic
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.config.settings import settings
from app.models.schemas import KnowledgeQuery, KnowledgeResponse
import logging

logger = logging.getLogger(__name__)

class ProductKnowledgeAgent:
    """Agent specialized in security product knowledge."""
    
    def __init__(self, product_type: str = "carbon_black"):
        """
        Initialize the Knowledge Agent.
        
        Args:
            product_type: Type of product to focus on ('prisma_cloud' or 'carbon_black')
        """
        logger.info("Initializing ProductKnowledgeAgent for %s", product_type)
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.product_type = product_type
        
        # Choose embeddings based on available API keys
        if settings.OPENAI_API_KEY:
            # Use OpenAI embeddings if key is provided
            try:
                from langchain_openai import OpenAIEmbeddings
                self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            except ImportError:
                # Fallback to HuggingFace embeddings if langchain_openai is not available
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            # Use HuggingFace embeddings as fallback
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Track processed URLs
        self.processed_urls = set()
        
        # Initialize with default product URLs
        self._initialize_with_default_urls()
        
    def _initialize_with_default_urls(self):
        """Initialize with default product URLs based on product type."""
        if self.product_type == "carbon_black":
            # Carbon Black URLs
            urls = [
                "https://www.broadcom.com/products/carbon-black",
                "https://www.broadcom.com/products/carbon-black/threat-prevention",
                "https://www.broadcom.com/products/carbon-black/threat-detection-and-response",
                "https://www.broadcom.com/products/carbon-black/threat-detection-and-response/endpoint-detection-and-response",
                "https://docs.broadcom.com/doc/Carbon-Black-EDR-Datasheet"
            ]
            print("Initializing Product Knowledge Agent with Carbon Black documentation...")
        else:
            # Prisma Cloud URLs
            urls = [
                "https://docs.prismacloud.io/en/enterprise-edition/rn/prisma-cloud-release-info",
                "https://docs.prismacloud.io/en/enterprise-edition/rn/features-introduced-in-2023",
                "https://docs.prismacloud.io/en/enterprise-edition/rn/features-introduced-in-2022"
            ]
            print("Initializing Product Knowledge Agent with Prisma Cloud documentation...")
            
        # Initialize with these URLs
        asyncio.create_task(self.initialize_with_multiple_urls(urls))
        
        # Add fallback product information in case URL scraping fails
        self._add_fallback_product_info()

    async def scrape_documentation(self, url: str) -> str:
        """
        Scrape the product documentation asynchronously.
        
        Args:
            url: URL of the documentation to scrape
            
        Returns:
            Extracted text content
        """
        logger.info("Scraping documentation from %s", url)
        try:
            print(f"Scraping {url}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unnecessary elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer']):
                element.decompose()
                
            # Get the main content
            text = soup.get_text(strip=True)
            print(f"Scraped {len(text)} characters of text from {url}")
            logger.info("Successfully scraped %d characters from %s", len(text), url)
            return text
        except Exception as e:
            logger.error("Error scraping documentation from %s: %s", url, e)
            return ""

    def process_documentation(self, text: str):
        """
        Process the documentation and create vector store.
        
        Args:
            text: Text content to process
        """
        logger.info("Processing documentation text of length %d", len(text) if text else 0)
        try:
            # Split text into chunks
            if not text:
                raise ValueError("No text to process")
                
            chunks = self.text_splitter.split_text(text)
            print(f"Split text into {len(chunks)} chunks")
            
            if not chunks:
                raise ValueError("No chunks created from text")
                
            # Create vector store
            if self.vector_store:
                # Add to existing store
                self.vector_store.add_texts(chunks)
            else:
                # Create new store
                self.vector_store = FAISS.from_texts(
                    texts=chunks,
                    embedding=self.embeddings
                )
            print(f"Processed {len(chunks)} chunks of documentation")
            logger.info("Processed %d chunks of documentation", len(chunks))
        except Exception as e:
            logger.error("Error processing documentation: %s", e)

    async def add_documentation(self, doc_url: str) -> bool:
        """
        Add additional documentation to the knowledge base.
        
        Args:
            doc_url: URL of the documentation to add
            
        Returns:
            Boolean indicating success
        """
        # Check if URL was already processed
        if doc_url in self.processed_urls:
            print(f"URL {doc_url} was already processed. Skipping.")
            return True
            
        print(f"Scraping additional documentation from {doc_url}...")
        text = await self.scrape_documentation(doc_url)
        
        if not text:
            print(f"Failed to scrape documentation from {doc_url}")
            return False
        
        print("Processing additional documentation...")
        try:
            # Process the documentation
            self.process_documentation(text)
            
            # Mark URL as processed
            self.processed_urls.add(doc_url)
            return True
        except Exception as e:
            print(f"Error processing additional documentation: {e}")
            return False

    async def initialize_with_multiple_urls(self, urls: List[str]):
        """
        Initialize the agent with multiple documentation URLs.
        
        Args:
            urls: List of documentation URLs to initialize with
        """
        logger.info("Initializing with multiple documentation URLs: %s", urls)
        success = False
        
        for url in urls:
            print(f"Processing URL: {url}")
            if not self.vector_store:
                # First URL - use normal initialization
                print("Initializing with first URL...")
                await self.initialize(url)
                if self.vector_store:
                    success = True
            else:
                # Additional URLs - add to existing knowledge base
                result = await self.add_documentation(url)
                success = success or result
        
        if success:
            print("Agent initialized successfully with multiple documentation sources!")
        else:
            print("Failed to initialize agent with any documentation. Using fallback data...")
            self._add_fallback_product_info()

    def query_knowledge_base(
        self, 
        query: str, 
        k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant context.
        
        Args:
            query: User query
            k: Number of relevant documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        logger.info("Querying knowledge base with query: '%s' (top %d)", query, k)
        if not self.vector_store:
            return []
            
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0)
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return []

    async def get_response(self, query: KnowledgeQuery) -> KnowledgeResponse:
        """
        Get a response to a user query using the knowledge base.
        
        Args:
            query: KnowledgeQuery object containing the user query
            
        Returns:
            KnowledgeResponse object with the agent's response
        """
        logger.info("Getting response for query: '%s'", query.query)
        try:
            # Query the knowledge base for relevant context
            relevant_docs = self.query_knowledge_base(query.query)
            
            # Build context from relevant documents
            context_text = ""
            if relevant_docs:
                context_text = "\n\n".join([doc["content"] for doc in relevant_docs])
            
            # Create system prompt
            system_prompt = f"""You are a knowledgeable assistant for {self.product_type.replace('_', ' ').title()} products. 
            Use the provided context to answer questions accurately and helpfully.
            
            Context:
            {context_text}
            
            Please provide a clear, accurate response based on the context provided."""
            
            # Get response from Claude
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": query.query
                    }
                ]
            )
            
            # Calculate confidence based on context relevance
            confidence = 0.8 if relevant_docs else 0.5
            
            return KnowledgeResponse(
                response=response.content[0].text,
                context=relevant_docs,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error("Error getting response: %s", e)
            return KnowledgeResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                context=[],
                confidence=0.0
            )

    async def initialize(self, doc_url: str):
        """
        Initialize the agent with a single documentation URL.
        
        Args:
            doc_url: URL of the documentation to initialize with
        """
        logger.info("Initializing agent with documentation URL: %s", doc_url)
        text = await self.scrape_documentation(doc_url)
        if text:
            self.process_documentation(text)
            self.processed_urls.add(doc_url)

    def _add_fallback_product_info(self):
        """Add fallback product information based on product type."""
        logger.info("Adding fallback product information for %s", self.product_type)
        fallback_text = []
        
        if self.product_type == "carbon_black":
            # Carbon Black fallback information
            fallback_text.append("Carbon Black is a cybersecurity solution now owned by Broadcom (previously VMware).")
            fallback_text.append("Carbon Black provides endpoint protection, detection and response capabilities.")
            fallback_text.append("Key products include Carbon Black EDR (Endpoint Detection and Response), Carbon Black Cloud, and Carbon Black App Control.")
            fallback_text.append("Carbon Black uses behavioral analytics, machine learning, and threat intelligence to detect and prevent attacks.")
            fallback_text.append("Carbon Black EDR provides continuous monitoring, threat hunting, and incident response capabilities.")
            fallback_text.append("Carbon Black Cloud is a cloud-native endpoint protection platform that combines antivirus, EDR, and threat hunting.")
            fallback_text.append("Carbon Black App Control provides application control and critical infrastructure protection.")
            fallback_text.append("Carbon Black integrates with many security tools and SOC platforms.")
        else:
            # Prisma Cloud fallback information
            fallback_text.append("Prisma Cloud is a comprehensive cloud native security platform from Palo Alto Networks.")
            fallback_text.append("It provides visibility and protection across the entire cloud native stack, from infrastructure to applications.")
            fallback_text.append("Key features include CSPM, CWPP, CIEM, and supply chain security.")
            fallback_text.append("Prisma Cloud integrates with CI/CD pipelines for shift-left security.")
            fallback_text.append("Prisma Cloud supports multiple cloud providers including AWS, Azure, and GCP.")
        
        # Add the fallback information to the knowledge base
        if fallback_text:
            combined_text = "\n\n".join(fallback_text)
            try:
                chunks = self.text_splitter.split_text(combined_text)
                if self.vector_store:
                    self.vector_store.add_texts(chunks)
                else:
                    self.vector_store = FAISS.from_texts(texts=chunks, embedding=self.embeddings)
                print(f"Added fallback product information to knowledge base.")
            except Exception as e:
                print(f"Error adding fallback information: {e}")

# Create singleton instance
knowledge_agent = ProductKnowledgeAgent() 