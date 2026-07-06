import { STORYLANE_BASE_URL } from './storylaneConfig';

export interface StorylaneSection {
  id: string;
  name: string;
  url: string;
  description: string;
  keywords: string[];
}

export interface DashboardMapping {
  question: string;
  section: string;
  url: string;
}

const URLS = {
  platforms: `${STORYLANE_BASE_URL}?page_id=8d6bd75d-b8fe-4691-b925-cdf616e84b9c`,
  apiAccess: `${STORYLANE_BASE_URL}?page_id=769cd63f-b3d4-4fdd-9513-472a7bd6730c`,
  alertsFileless: 'https://app.storylane.io/preview/7a1bec8b-70e8-4b94-a3f0-3a77dfcd5969',
  alertsPrioritized: `${STORYLANE_BASE_URL}?page_id=2552848c-8c2a-4b6d-b421-e8f9d780eced`,
  policies: `${STORYLANE_BASE_URL}?page_id=9a80dff6-0cb1-42e0-82ab-d4fc6b50ad40`,
  malwareRemoval: 'https://app.storylane.io/preview/7a1bec8b-70e8-4b94-a3f0-3a77dfcd5969',
  mainDashboard: STORYLANE_BASE_URL,
};

export class StorylaneMapper {
  private sections: Map<string, StorylaneSection> = new Map();
  private questionMappings: Map<string, DashboardMapping> = new Map();

  constructor() {
    this.initializeSections();
    this.initializeQuestionMappings();
  }

  private initializeSections(): void {
    const sections: StorylaneSection[] = [
      {
        id: 'settings',
        name: 'Settings',
        url: URLS.mainDashboard,
        description: 'Configuration, API access, and platform support information',
        keywords: ['settings', 'configuration', 'api', 'integrations', 'custom', 'management console', 'console', 'management', 'configure', 'setup', 'access', 'admin', 'administrative', 'platforms', 'operating systems', 'windows', 'macos', 'linux', 'endpoints', 'deploy', 'deployment', 'supported', 'support', 'systems', 'platform', 'os', 'operating system']
      },
      {
        id: 'alerts',
        name: 'Alerts',
        url: URLS.alertsPrioritized,
        description: 'Alert management and fileless attack detection',
        keywords: ['alerts', 'fileless', 'living off the land', 'lotl', 'prioritization', 'tuning', 'noise', 'detect', 'detection', 'threats', 'attacks', 'malicious', 'suspicious', 'monitoring', 'security']
      },
      {
        id: 'enforce-policies',
        name: 'Enforce -> Policies',
        url: URLS.policies,
        description: 'Automated response actions and policy enforcement',
        keywords: ['automated', 'response', 'actions', 'quarantine', 'kill process', 'isolate', 'policies', 'enforce', 'enforcement', 'respond', 'block', 'prevent', 'stop', 'contain', 'mitigate']
      },
      {
        id: 'malware-removal',
        name: 'Enforce -> Malware removal',
        url: URLS.malwareRemoval,
        description: 'Malware detection and removal capabilities',
        keywords: ['malware', 'removal', 'detection', 'removed', 'cleanup', 'virus', 'viruses', 'clean', 'remove', 'delete', 'eradicate', 'eliminate']
      }
    ];

    sections.forEach(section => {
      this.sections.set(section.id, section);
    });
  }

  private initializeQuestionMappings(): void {
    const mappings: DashboardMapping[] = [
      {
        question: 'What platforms and operating systems are supported (Windows, macOS, Linux)?',
        section: 'Settings',
        url: URLS.platforms
      },
      {
        question: 'Is there API access for custom integrations?',
        section: 'Settings',
        url: URLS.apiAccess
      },
      {
        question: 'How does Carbon Black detect and respond to fileless or living-off-the-land (LotL) attacks?',
        section: 'Alerts',
        url: URLS.alertsFileless
      },
      {
        question: 'What automated response actions are available (e.g., quarantine, kill process, isolate host)?',
        section: 'Enforce -> Policies',
        url: URLS.policies
      },
      {
        question: 'How can I look for removed malware?',
        section: 'Enforce -> Malware removal',
        url: URLS.malwareRemoval
      },
      {
        question: 'What does the management console look like? (Ask for a walkthrough.)',
        section: 'Settings',
        url: URLS.mainDashboard
      },
      {
        question: 'How are alerts prioritized and tuned to reduce noise?',
        section: 'Alerts',
        url: URLS.alertsPrioritized
      },
      {
        question: 'show me the endpoints',
        section: 'Settings',
        url: URLS.platforms
      },
      {
        question: 'show me the settings',
        section: 'Settings',
        url: URLS.mainDashboard
      },
      {
        question: 'show me the alerts',
        section: 'Alerts',
        url: URLS.alertsPrioritized
      },
      {
        question: 'show me the policies',
        section: 'Enforce -> Policies',
        url: URLS.policies
      },
      {
        question: 'show me malware removal',
        section: 'Enforce -> Malware removal',
        url: URLS.malwareRemoval
      },
      {
        question: 'how is carbon black deployed',
        section: 'Settings',
        url: URLS.platforms
      },
      {
        question: 'what platforms are supported',
        section: 'Settings',
        url: URLS.platforms
      },
      {
        question: 'api access for custom integrations',
        section: 'Settings',
        url: URLS.apiAccess
      },
      {
        question: 'for remove malware',
        section: 'Enforce -> Malware removal',
        url: URLS.malwareRemoval
      }
    ];

    mappings.forEach(mapping => {
      this.questionMappings.set(mapping.question.toLowerCase(), mapping);
    });
  }

  mapQueryToSection(query: string): StorylaneSection | null {
    const normalizedQuery = query.toLowerCase().trim();
    console.log(`[StorylaneMapper] Mapping query: "${query}"`);
    console.log(`[StorylaneMapper] Normalized query: "${normalizedQuery}"`);

    // First, try exact question matching (use mapping-specific URL)
    for (const [question, mapping] of Array.from(this.questionMappings)) {
      console.log(`[StorylaneMapper] Checking question: "${question}"`);
      if (normalizedQuery.includes(question) || question.includes(normalizedQuery)) {
        const section = this.sections.get(this.getSectionIdFromName(mapping.section));
        if (section) {
          console.log(`[StorylaneMapper] Exact match found: ${section.name}`);
          return { ...section, url: mapping.url };
        }
      }
    }

    // Then, try keyword matching with improved scoring
    let bestMatch: StorylaneSection | null = null;
    let bestScore = 0;
    const keywordMatches: { [key: string]: number } = {};

    for (const section of Array.from(this.sections.values())) {
      let score = 0;

      for (const keyword of section.keywords) {
        if (normalizedQuery.includes(keyword)) {
          const keywordScore = keyword.length + (keyword.split(' ').length * 2);
          score += keywordScore;
        }
      }

      keywordMatches[section.name] = score;

      if (score > bestScore) {
        bestScore = score;
        bestMatch = section;
      }
    }

    console.log(`[StorylaneMapper] Keyword scores:`, keywordMatches);
    console.log(`[StorylaneMapper] Best match: ${bestMatch?.name} (score: ${bestScore})`);

    return bestMatch;
  }

  private getSectionIdFromName(sectionName: string): string {
    for (const [id, section] of Array.from(this.sections)) {
      if (section.name === sectionName) {
        return id;
      }
    }
    return '';
  }

  getAllSections(): StorylaneSection[] {
    return Array.from(this.sections.values());
  }

  getSectionById(id: string): StorylaneSection | null {
    return this.sections.get(id) || null;
  }

  getAllMappings(): DashboardMapping[] {
    return Array.from(this.questionMappings.values());
  }
}
