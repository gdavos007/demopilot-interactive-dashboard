import { StorylaneMapper, StorylaneSection } from './storylaneMapper';
import { STORYLANE_BASE_URL } from './storylaneConfig';

export interface NavigationEvent {
  type: 'navigate' | 'highlight' | 'reset';
  section?: StorylaneSection;
  url?: string;
  timestamp: Date;
  source: 'chat' | 'voice' | 'manual';
}

export class StorylaneController {
  private mapper: StorylaneMapper;
  private currentSection: StorylaneSection | null = null;
  private listeners: Set<(event: NavigationEvent) => void> = new Set();
  private iframeRef: React.RefObject<HTMLIFrameElement> | null = null;

  constructor() {
    this.mapper = new StorylaneMapper();
  }

  setIframeRef(ref: React.RefObject<HTMLIFrameElement>): void {
    console.log(`[StorylaneController] Setting iframe ref:`, ref);
    console.log(`[StorylaneController] Iframe ref current:`, ref?.current);
    this.iframeRef = ref;
    console.log(`[StorylaneController] Iframe ref set successfully`);
  }

  // Debug method to manually test navigation
  debugNavigateToSection(sectionName: string): void {
    console.log(`[StorylaneController] DEBUG: Manual navigation to ${sectionName}`);
    const section = this.mapper.getSectionById(sectionName.toLowerCase().replace(/\s+/g, '-'));
    if (section) {
      console.log(`[StorylaneController] DEBUG: Found section:`, section);
      this.navigateToSection(section, 'manual');
    } else {
      console.log(`[StorylaneController] DEBUG: Section not found. Available sections:`, this.mapper.getAllSections().map(s => s.id));
    }
  }

  // Debug method to get current iframe state
  debugGetIframeState(): any {
    return {
      iframeRef: this.iframeRef,
      iframeCurrent: this.iframeRef?.current,
      iframeSrc: this.iframeRef?.current?.src,
      currentSection: this.currentSection,
      availableSections: this.mapper.getAllSections()
    };
  }

  handleQuery(query: string, source: 'chat' | 'voice' | 'manual' = 'manual'): void {
    console.log(`[StorylaneController] Handling query from ${source}: "${query}"`);
    const section = this.mapper.mapQueryToSection(query);
    
    console.log(`[StorylaneController] Mapper returned section:`, section);
    
    if (section) {
      console.log(`[StorylaneController] Navigating to section: ${section.name}`);
      console.log(`[StorylaneController] About to call navigateToSection...`);
      this.navigateToSection(section, source);
      console.log(`[StorylaneController] navigateToSection call completed`);
    } else {
      console.log(`[StorylaneController] No matching section found for query: "${query}"`);
      // If no specific section found, show a helpful message
      this.showNoMatchMessage(query);
    }
  }

  navigateToSection(section: StorylaneSection, source: 'chat' | 'voice' | 'manual' = 'manual'): void {
    this.currentSection = section;
    
    console.log(`[StorylaneController] Attempting to navigate to: ${section.name}`);
    console.log(`[StorylaneController] URL: ${section.url}`);
    console.log(`[StorylaneController] Iframe ref exists: ${!!this.iframeRef?.current}`);
    console.log(`[StorylaneController] Iframe ref current:`, this.iframeRef?.current);
    console.log(`[StorylaneController] Iframe ref object:`, this.iframeRef);
    
    // If iframe ref is not ready, wait for it
    if (!this.iframeRef?.current) {
      console.log(`[StorylaneController] Iframe ref not ready, waiting...`);
      this.waitForIframeAndNavigate(section, source);
      return;
    }
    
    console.log(`[StorylaneController] Iframe ref ready, proceeding with navigation...`);
    this.performNavigation(section, source);
  }

  private waitForIframeAndNavigate(section: StorylaneSection, source: 'chat' | 'voice' | 'manual', maxRetries: number = 10): void {
    let retries = 0;
    
    const checkIframe = () => {
      retries++;
      console.log(`[StorylaneController] Checking iframe ref (attempt ${retries}/${maxRetries})...`);
      
      if (this.iframeRef?.current) {
        console.log(`[StorylaneController] Iframe ref is now ready!`);
        this.performNavigation(section, source);
      } else if (retries < maxRetries) {
        console.log(`[StorylaneController] Iframe ref still not ready, retrying in 100ms...`);
        setTimeout(checkIframe, 100);
      } else {
        console.error(`[StorylaneController] Iframe ref never became ready after ${maxRetries} attempts`);
      }
    };
    
    checkIframe();
  }

  private performNavigation(section: StorylaneSection, source: 'chat' | 'voice' | 'manual'): void {
    console.log(`[StorylaneController] Performing navigation to: ${section.name}`);
    
    // Force reload approach - completely recreate the iframe
    if (this.iframeRef?.current) {
      console.log(`[StorylaneController] Force reloading iframe with: ${section.url}`);
      
      const iframe = this.iframeRef.current;
      const parent = iframe.parentElement;
      
      if (parent) {
        console.log(`[StorylaneController] Removing old iframe...`);
        parent.removeChild(iframe);
        
        console.log(`[StorylaneController] Creating new iframe...`);
        const newIframe = document.createElement('iframe');
        newIframe.src = section.url;
        newIframe.style.border = 'none';
        newIframe.style.height = '100%';
        newIframe.style.width = '100%';
        newIframe.title = 'Interactive Carbon Black Dashboard';
        newIframe.key = 'storylane-iframe';
        
        console.log(`[StorylaneController] Appending new iframe...`);
        parent.appendChild(newIframe);
        
        console.log(`[StorylaneController] Updating iframe ref...`);
        this.iframeRef.current = newIframe;
        
        console.log(`[StorylaneController] Force reload completed`);
      } else {
        console.error(`[StorylaneController] No parent element found`);
      }
    } else {
      console.error(`[StorylaneController] Iframe ref is still null during navigation`);
    }

    // Create navigation event
    const event: NavigationEvent = {
      type: 'navigate',
      section: section,
      url: section.url,
      timestamp: new Date(),
      source: source
    };

    // Notify listeners
    this.notifyListeners(event);

    // Show navigation feedback
    this.showNavigationFeedback(section, source);
  }

  navigateToUrl(url: string, source: 'chat' | 'voice' | 'manual' = 'manual'): void {
    // Navigate the iframe to the new URL
    if (this.iframeRef?.current) {
      this.iframeRef.current.src = url;
    }

    // Create navigation event
    const event: NavigationEvent = {
      type: 'navigate',
      url: url,
      timestamp: new Date(),
      source: source
    };

    // Notify listeners
    this.notifyListeners(event);
  }

  resetDashboard(source: 'chat' | 'voice' | 'manual' = 'manual'): void {
    console.log(`[StorylaneController] Resetting dashboard to main view`);
    
    // Reset to the main dashboard URL (base URL without pageid)
    const mainUrl = STORYLANE_BASE_URL;
    
    // Use force reload approach for reset too
    if (this.iframeRef?.current) {
      console.log(`[StorylaneController] Force reloading iframe with: ${mainUrl}`);
      
      const iframe = this.iframeRef.current;
      const parent = iframe.parentElement;
      
      if (parent) {
        console.log(`[StorylaneController] Removing old iframe...`);
        parent.removeChild(iframe);
        
        console.log(`[StorylaneController] Creating new iframe...`);
        const newIframe = document.createElement('iframe');
        newIframe.src = mainUrl;
        newIframe.style.border = 'none';
        newIframe.style.height = '100%';
        newIframe.style.width = '100%';
        newIframe.title = 'Interactive Carbon Black Dashboard';
        newIframe.key = 'storylane-iframe';
        
        console.log(`[StorylaneController] Appending new iframe...`);
        parent.appendChild(newIframe);
        
        console.log(`[StorylaneController] Updating iframe ref...`);
        this.iframeRef.current = newIframe;
        
        console.log(`[StorylaneController] Reset force reload completed`);
      } else {
        console.error(`[StorylaneController] No parent element found for reset`);
      }
    } else {
      console.error(`[StorylaneController] Cannot reset - iframe ref is null`);
    }

    this.currentSection = null;

    // Create reset event
    const event: NavigationEvent = {
      type: 'reset',
      url: mainUrl,
      timestamp: new Date(),
      source: source
    };

    // Notify listeners
    this.notifyListeners(event);
  }

  private showNavigationFeedback(section: StorylaneSection, source: string): void {
    try {
      console.log(`[StorylaneController] Showing navigation feedback for: ${section.name}`);
      
      // Create a temporary notification
      const notification = document.createElement('div');
      notification.className = 'storylane-navigation-feedback';
      notification.innerHTML = `
        <div class="feedback-content">
          <strong>Navigating to:</strong> ${section.name}
          <br>
          <small>${section.description}</small>
          <br>
          <small>Source: ${source}</small>
        </div>
      `;
      
      document.body.appendChild(notification);

      // Auto-remove after 3 seconds
      setTimeout(() => {
        try {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        } catch (error) {
          console.error('[StorylaneController] Error removing notification:', error);
        }
      }, 3000);
    } catch (error) {
      console.error('[StorylaneController] Error showing navigation feedback:', error);
    }
  }

  private showNoMatchMessage(query: string): void {
    try {
      console.log(`[StorylaneController] Showing no match message for: "${query}"`);
      
      const notification = document.createElement('div');
      notification.className = 'storylane-no-match-feedback';
      notification.innerHTML = `
        <div class="feedback-content">
          <strong>No specific section found for:</strong> "${query}"
          <br>
          <small>Try asking about platforms, alerts, policies, or malware removal</small>
        </div>
      `;
      
      document.body.appendChild(notification);

      // Auto-remove after 5 seconds
      setTimeout(() => {
        try {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        } catch (error) {
          console.error('[StorylaneController] Error removing no-match notification:', error);
        }
      }, 5000);
    } catch (error) {
      console.error('[StorylaneController] Error showing no match message:', error);
    }
  }

  // Event listeners
  addNavigationListener(listener: (event: NavigationEvent) => void): void {
    this.listeners.add(listener);
  }

  removeNavigationListener(listener: (event: NavigationEvent) => void): void {
    this.listeners.delete(listener);
  }

  private notifyListeners(event: NavigationEvent): void {
    console.log(`[StorylaneController] Notifying ${this.listeners.size} listeners of event:`, event);
    this.listeners.forEach((listener, index) => {
      try {
        listener(event);
        console.log(`[StorylaneController] Listener ${index} handled event successfully`);
      } catch (error) {
        console.error(`[StorylaneController] Error in navigation listener ${index}:`, error);
      }
    });
  }

  // Utility methods
  getCurrentSection(): StorylaneSection | null {
    return this.currentSection;
  }

  getMapper(): StorylaneMapper {
    return this.mapper;
  }

  // Predefined navigation methods for common queries
  showPlatformSupport(): void {
    const section = this.mapper.getSectionById('inventory-endpoints');
    if (section) {
      this.navigateToSection(section, 'manual');
    }
  }

  showApiSettings(): void {
    const section = this.mapper.getSectionById('settings');
    if (section) {
      this.navigateToSection(section, 'manual');
    }
  }

  showAlerts(): void {
    const section = this.mapper.getSectionById('alerts');
    if (section) {
      this.navigateToSection(section, 'manual');
    }
  }

  showPolicies(): void {
    const section = this.mapper.getSectionById('enforce-policies');
    if (section) {
      this.navigateToSection(section, 'manual');
    }
  }

  showMalwareRemoval(): void {
    const section = this.mapper.getSectionById('malware-removal');
    if (section) {
      this.navigateToSection(section, 'manual');
    }
  }
}
