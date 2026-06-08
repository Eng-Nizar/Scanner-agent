"""
Keywords Configuration - Choose your sector focus!
Easily swap between Defense, Space, AI, Cybersecurity, etc.
"""

# ============================================================================
# SECTOR KEYWORD DEFINITIONS
# ============================================================================

SECTOR_KEYWORDS = {
    'defense': {
        'name': '🛡️ Defense/Government Contractors',
        'primary_keywords': [
            'pentagon', 'dod', 'nasa', 'government', 'defense',
            'military', 'contract', 'federal', 'classified',
            'aerospace', 'defense contractor', 'weapons',
            'u.s. government', 'us government', 'armed forces',
            'army', 'navy', 'air force', 'marine corps'
        ],
        'industries': [
            'defense', 'aerospace', 'security', 'cybersecurity',
            'drone', 'satellite', 'intelligence', 'military',
            'space technology', 'defense contractors', 'aerospace & defense',
            'guided missiles', 'aircraft', 'weapons systems'
        ],
        'tailwinds': [
            'defense', 'cybersecurity', 'drone', 'space', 'satellite',
            'autonomous', 'defense contractor', 'aerospace', 'pentagon',
            'armed forces', 'intelligence', 'military tech', 'ai'
        ]
    },
    
    'space': {
        'name': '🚀 Space/Aerospace/Satellite',
        'primary_keywords': [
            'space', 'satellite', 'launch', 'orbital', 'rocket',
            'spacecraft', 'propulsion', 'aerospace', 'nasa', 'satellite',
            'constellation', 'earth observation', 'communications satellite',
            'space technology', 'spaceflight', 'reusable', 'payload'
        ],
        'industries': [
            'space technology', 'aerospace', 'aerospace & defense',
            'satellite communications', 'space exploration',
            'aircraft', 'drone', 'propulsion systems'
        ],
        'tailwinds': [
            'space', 'satellite', 'launch', 'rocket', 'orbital',
            'nasa', 'spacecraft', 'earth observation', 'communications',
            'autonomous', 'ai', 'machine learning', 'constellation'
        ]
    },
    
    'ai': {
        'name': '🤖 AI / Machine Learning',
        'primary_keywords': [
            'artificial intelligence', 'ai', 'machine learning', 'ml',
            'deep learning', 'neural network', 'algorithm', 'data',
            'nlp', 'computer vision', 'ai platform', 'large language model',
            'llm', 'generative ai', 'foundation model', 'transformer'
        ],
        'industries': [
            'software', 'technology', 'artificial intelligence',
            'machine learning', 'data analytics', 'cloud computing',
            'saas', 'enterprise software', 'ai services'
        ],
        'tailwinds': [
            'ai', 'artificial intelligence', 'machine learning',
            'deep learning', 'data', 'analytics', 'cloud', 'automation',
            'efficiency', 'productivity', 'transformation', 'digital'
        ]
    },
    
    'cybersecurity': {
        'name': '🔒 Cybersecurity',
        'primary_keywords': [
            'cybersecurity', 'cyber', 'security', 'threat', 'breach',
            'endpoint', 'vulnerability', 'penetration', 'malware',
            'ransomware', 'zero-trust', 'network security', 'firewall',
            'encryption', 'identity', 'access management', 'siem'
        ],
        'industries': [
            'cybersecurity', 'security', 'software', 'technology',
            'information technology', 'cloud security', 'managed security',
            'security services', 'incident response'
        ],
        'tailwinds': [
            'cybersecurity', 'cyber threat', 'security', 'breach',
            'ransomware', 'zero-trust', 'cloud', 'ai', 'machine learning',
            'automation', 'threat detection', 'compliance', 'regulation'
        ]
    },
    
    'biotech': {
        'name': '🧬 Biotech / Pharma',
        'primary_keywords': [
            'biotech', 'pharmaceutical', 'drug', 'fda', 'clinical trial',
            'gene therapy', 'cell therapy', 'vaccine', 'therapeutic',
            'biotechnology', 'protein', 'genomics', 'crispr', 'mrna'
        ],
        'industries': [
            'biotechnology', 'pharmaceutical', 'life sciences',
            'healthcare', 'medical devices', 'diagnostics',
            'therapeutic', 'drug development'
        ],
        'tailwinds': [
            'gene therapy', 'cell therapy', 'vaccine', 'fda approval',
            'clinical success', 'genomics', 'crispr', 'mrna',
            'personalized medicine', 'rare disease', 'pandemic'
        ]
    },
    
    'renewable_energy': {
        'name': '⚡ Renewable Energy / Clean Tech',
        'primary_keywords': [
            'renewable', 'solar', 'wind', 'energy', 'battery',
            'electric vehicle', 'ev', 'charging', 'grid', 'storage',
            'sustainability', 'clean energy', 'carbon', 'emissions',
            'hydrogen', 'fuel cell'
        ],
        'industries': [
            'renewable energy', 'solar', 'wind', 'electric vehicles',
            'battery technology', 'clean technology', 'energy storage',
            'smart grid', 'utilities'
        ],
        'tailwinds': [
            'solar', 'wind', 'electric vehicle', 'battery', 'renewable',
            'net zero', 'carbon neutral', 'climate', 'regulation',
            'subsidy', 'grid modernization', 'sustainability'
        ]
    },
    
    'cloud': {
        'name': '☁️ Cloud / SaaS',
        'primary_keywords': [
            'cloud', 'saas', 'software-as-a-service', 'paas', 'iaas',
            'cloud computing', 'serverless', 'containerization', 'kubernetes',
            'microservices', 'api', 'platform', 'infrastructure'
        ],
        'industries': [
            'cloud computing', 'saas', 'enterprise software',
            'software', 'technology', 'information technology',
            'data services', 'platform services'
        ],
        'tailwinds': [
            'cloud migration', 'digital transformation', 'remote work',
            'scalability', 'cost efficiency', 'ai integration',
            'automation', 'data analytics', 'api-first'
        ]
    },
    
    'semiconductor': {
        'name': '🔌 Semiconductors / Chips',
        'primary_keywords': [
            'semiconductor', 'chip', 'processor', 'gpu', 'cpu',
            'fab', 'foundry', 'wafer', 'ai accelerator', 'edge',
            'semiconductor manufacturing', 'ic', 'transistor'
        ],
        'industries': [
            'semiconductors', 'semiconductor equipment', 'semiconductor materials',
            'fabless', 'foundry', 'integrated circuits', 'processors'
        ],
        'tailwinds': [
            'ai', 'data center', 'gpu', 'chip shortage', 'advanced node',
            'manufacturing', '5g', 'iot', 'autonomous', 'edge computing'
        ]
    },
    
    'healthcare_tech': {
        'name': '⚕️ Healthcare / MedTech',
        'primary_keywords': [
            'healthcare', 'medical', 'diagnostic', 'hospital', 'clinical',
            'patient', 'treatment', 'telemedicine', 'ehr', 'prescription',
            'medtech', 'medical device', 'health technology'
        ],
        'industries': [
            'healthcare', 'medical devices', 'health information technology',
            'healthcare services', 'diagnostics', 'medical equipment',
            'telehealth', 'home health'
        ],
        'tailwinds': [
            'aging population', 'chronic disease', 'telemedicine',
            'ai diagnostics', 'remote monitoring', 'personalized medicine',
            'healthcare reform', 'digital health', 'reimbursement'
        ]
    },
    
    'fintech': {
        'name': '💰 FinTech / Finance',
        'primary_keywords': [
            'fintech', 'financial', 'blockchain', 'cryptocurrency', 'bitcoin',
            'payment', 'lending', 'trading', 'wealth', 'crypto', 'defi',
            'web3', 'nft', 'digital currency'
        ],
        'industries': [
            'financial services', 'fintech', 'payment processing',
            'financial software', 'lending', 'investment management',
            'cryptocurrency', 'blockchain'
        ],
        'tailwinds': [
            'digital payment', 'blockchain', 'crypto adoption',
            'automation', 'ai trading', 'cbdc', 'defi', 'web3',
            'regulatory clarity', 'institutional adoption'
        ]
    }
}

# ============================================================================
# CURRENT SECTOR SELECTION
# ============================================================================

# Change this to switch sectors!
# Options: 'defense', 'space', 'ai', 'cybersecurity', 'biotech',
#          'renewable_energy', 'cloud', 'semiconductor', 'healthcare_tech', 'fintech'

DEFAULT_SECTOR = 'defense'

# ============================================================================
# FUNCTIONS TO GET KEYWORDS
# ============================================================================

def get_current_sector_config():
    """Get current sector configuration"""
    return SECTOR_KEYWORDS.get(DEFAULT_SECTOR, SECTOR_KEYWORDS['defense'])

def get_primary_keywords():
    """Get primary keywords for current sector"""
    return get_current_sector_config()['primary_keywords']

def get_industry_keywords():
    """Get industry keywords for current sector"""
    return get_current_sector_config()['industries']

def get_tailwind_keywords():
    """Get tailwind keywords for current sector"""
    return get_current_sector_config()['tailwinds']

def get_sector_name():
    """Get friendly name of current sector"""
    return get_current_sector_config()['name']

def list_available_sectors():
    """List all available sectors"""
    return {sector: config['name'] for sector, config in SECTOR_KEYWORDS.items()}

def switch_sector(sector_name):
    """Switch to a different sector (updates DEFAULT_SECTOR)"""
    global DEFAULT_SECTOR
    if sector_name in SECTOR_KEYWORDS:
        DEFAULT_SECTOR = sector_name
        print(f"✅ Switched to {get_sector_name()}")
        return True
    else:
        print(f"❌ Sector '{sector_name}' not found!")
        print(f"Available sectors: {list(SECTOR_KEYWORDS.keys())}")
        return False

# ============================================================================
# QUICK REFERENCE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📊 AVAILABLE SECTORS")
    print("="*70 + "\n")
    
    for sector, name in list_available_sectors().items():
        print(f"  • {name}")
        print(f"    └─ Code: '{sector}'\n")
    
    print("="*70)
    print(f"CURRENTLY SELECTED: {get_sector_name()}")
    print("="*70)
    print("\nTo switch sectors, edit keywords_config.py:")
    print("  DEFAULT_SECTOR = 'space'  # or any other sector")
