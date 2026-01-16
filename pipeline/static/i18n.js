/**
 * Internationalization (i18n) Module for Review Graph Visualization
 * Supports multiple languages: English (en), Traditional Chinese (zh-TW)
 * 
 * Uses python-i18n backend with JSON translation files.
 * Fetches translations from /api/translations endpoint.
 * 
 * Usage:
 *   1. Include this file in HTML:
 *      <script src="/static/i18n.js"></script>
 *   
 *   2. Use data-i18n attributes in HTML:
 *      <span data-i18n="login.title">Default Text</span>
 *   
 *   3. Use in JavaScript:
 *      const text = i18n.t('login.title');
 */

// Translations cache
let translations = {};
let translationsLoaded = false;

// Current language (default: English)
let currentLanguage = localStorage.getItem('i18n-language') || 'en';

// Available languages
const availableLanguages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'zh-TW', name: '繁體中文', flag: '🇹🇼' }
];

/**
 * Load translations from server
 * @param {string} locale - Language code
 * @returns {Promise} Promise that resolves when translations are loaded
 */
async function loadTranslations(locale) {
    try {
        const response = await fetch(`/api/translations?locale=${locale}`);
        if (response.ok) {
            translations = await response.json();
            translationsLoaded = true;
            console.log(`i18n: Loaded translations for ${locale}`, Object.keys(translations).length, 'keys');
            return translations;
        } else {
            console.error('i18n: Failed to load translations', response.status);
        }
    } catch (error) {
        console.error('i18n: Error loading translations', error);
    }
    return {};
}

/**
 * Get nested value from object using dot notation
 * @param {object} obj - Object to search
 * @param {string} key - Dot-separated key (e.g., 'login.title')
 * @returns {string|undefined} Value or undefined
 */
function getNestedValue(obj, key) {
    return key.split('.').reduce((o, k) => (o && o[k] !== undefined) ? o[k] : undefined, obj);
}

/**
 * Get translation for a key
 * @param {string} key - Translation key (e.g., 'login.title')
 * @param {object} params - Optional parameters for interpolation
 * @returns {string} Translated text or key if not found
 */
function t(key, params = {}) {
    let text = getNestedValue(translations, key) || key;
    
    // Replace parameters {param} with values
    Object.keys(params).forEach(param => {
        text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), params[param]);
    });
    
    return text;
}

/**
 * Set current language
 * @param {string} langCode - Language code (e.g., 'en', 'zh-TW')
 */
async function setLanguage(langCode) {
    if (availableLanguages.some(l => l.code === langCode)) {
        currentLanguage = langCode;
        localStorage.setItem('i18n-language', langCode);
        await loadTranslations(langCode);
        applyTranslations();
        
        // Dispatch custom event for components that need to react
        window.dispatchEvent(new CustomEvent('languageChange', { detail: { language: langCode } }));
    }
}

/**
 * Get current language
 * @returns {string} Current language code
 */
function getLanguage() {
    return currentLanguage;
}

/**
 * Get available languages
 * @returns {Array} Available languages
 */
function getAvailableLanguages() {
    return availableLanguages;
}

/**
 * Apply translations to all elements with data-i18n attribute
 */
function applyTranslations() {
    // Debug: log translation status
    console.log('i18n: Applying translations, current language:', currentLanguage);
    console.log('i18n: Translations loaded:', translationsLoaded);
    console.log('i18n: Sample key test - correlation.table_avg_score:', t('correlation.table_avg_score'));
    
    // Translate text content
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translated = t(key);
        // Always update - the default text is in HTML anyway
        element.textContent = translated;
    });
    
    // Translate placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        const translated = t(key);
        element.placeholder = translated;
    });
    
    // Translate titles
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.title = t(key);
    });
    
    // Translate aria-labels
    document.querySelectorAll('[data-i18n-aria]').forEach(element => {
        const key = element.getAttribute('data-i18n-aria');
        element.setAttribute('aria-label', t(key));
    });
    
    // Update page title if specified
    const titleKey = document.body.getAttribute('data-i18n-page-title');
    if (titleKey) {
        document.title = t(titleKey);
    }
    
    // Update HTML lang attribute
    document.documentElement.lang = currentLanguage === 'zh-TW' ? 'zh-TW' : 'en';
}

/**
 * Create language switcher component
 * @param {string} containerId - ID of container element
 * @param {object} options - Options for styling
 */
function createLanguageSwitcher(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const { style = 'dropdown', showFlags = true, showNames = true } = options;
    
    if (style === 'dropdown') {
        const currentLang = availableLanguages.find(l => l.code === currentLanguage) || availableLanguages[0];
        
        container.innerHTML = `
            <div class="language-switcher">
                <button class="lang-toggle" id="langToggle" aria-label="Select language">
                    ${showFlags ? currentLang.flag : ''} ${showNames ? currentLang.name : ''}
                    <span class="lang-arrow">▼</span>
                </button>
                <div class="lang-dropdown" id="langDropdown">
                    ${availableLanguages.map(lang => `
                        <button class="lang-option ${lang.code === currentLanguage ? 'active' : ''}" 
                                data-lang="${lang.code}">
                            ${showFlags ? lang.flag : ''} ${lang.name}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Add styles if not already present
        if (!document.getElementById('i18n-styles')) {
            const styleEl = document.createElement('style');
            styleEl.id = 'i18n-styles';
            styleEl.textContent = `
                .language-switcher {
                    position: relative;
                    display: inline-block;
                }
                .lang-toggle {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    padding: 8px 12px;
                    background: rgba(255,255,255,0.15);
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 6px;
                    color: inherit;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s;
                }
                .lang-toggle:hover {
                    background: rgba(255,255,255,0.25);
                }
                .lang-arrow {
                    font-size: 10px;
                    transition: transform 0.3s;
                }
                .language-switcher.open .lang-arrow {
                    transform: rotate(180deg);
                }
                .lang-dropdown {
                    position: absolute;
                    top: 100%;
                    right: 0;
                    margin-top: 4px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(-10px);
                    transition: all 0.3s;
                    z-index: 1000;
                    min-width: 140px;
                    overflow: hidden;
                }
                .language-switcher.open .lang-dropdown {
                    opacity: 1;
                    visibility: visible;
                    transform: translateY(0);
                }
                .lang-option {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    width: 100%;
                    padding: 10px 15px;
                    border: none;
                    background: none;
                    color: #333;
                    cursor: pointer;
                    font-size: 14px;
                    text-align: left;
                    transition: background 0.2s;
                }
                .lang-option:hover {
                    background: #f5f5f5;
                }
                .lang-option.active {
                    background: #667eea;
                    color: white;
                }
            `;
            document.head.appendChild(styleEl);
        }
        
        // Event listeners
        const toggle = document.getElementById('langToggle');
        const dropdown = document.getElementById('langDropdown');
        const switcher = container.querySelector('.language-switcher');
        
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            switcher.classList.toggle('open');
        });
        
        dropdown.querySelectorAll('.lang-option').forEach(btn => {
            btn.addEventListener('click', () => {
                setLanguage(btn.dataset.lang);
                switcher.classList.remove('open');
                
                // Update toggle text
                const lang = availableLanguages.find(l => l.code === btn.dataset.lang);
                toggle.innerHTML = `${showFlags ? lang.flag : ''} ${showNames ? lang.name : ''} <span class="lang-arrow">▼</span>`;
                
                // Update active state
                dropdown.querySelectorAll('.lang-option').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            switcher.classList.remove('open');
        });
    } else if (style === 'buttons') {
        container.innerHTML = `
            <div class="language-buttons">
                ${availableLanguages.map(lang => `
                    <button class="lang-btn ${lang.code === currentLanguage ? 'active' : ''}" 
                            data-lang="${lang.code}">
                        ${showFlags ? lang.flag : ''} ${showNames ? lang.name : ''}
                    </button>
                `).join('')}
            </div>
        `;
        
        // Add styles
        if (!document.getElementById('i18n-btn-styles')) {
            const styleEl = document.createElement('style');
            styleEl.id = 'i18n-btn-styles';
            styleEl.textContent = `
                .language-buttons {
                    display: flex;
                    gap: 8px;
                }
                .lang-btn {
                    padding: 6px 12px;
                    background: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 4px;
                    color: inherit;
                    cursor: pointer;
                    font-size: 13px;
                    transition: all 0.3s;
                }
                .lang-btn:hover {
                    background: rgba(255,255,255,0.2);
                }
                .lang-btn.active {
                    background: rgba(255,255,255,0.3);
                    border-color: rgba(255,255,255,0.5);
                }
            `;
            document.head.appendChild(styleEl);
        }
        
        container.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                setLanguage(btn.dataset.lang);
                container.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }
}

/**
/**
 * Initialize i18n on page load
 */
async function initI18n() {
    // Load translations from server
    await loadTranslations(currentLanguage);
    
    // Apply translations when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => applyTranslations());
    } else {
        applyTranslations();
    }
}

// Auto-initialize
initI18n();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { t, setLanguage, getLanguage, getAvailableLanguages, createLanguageSwitcher, applyTranslations, loadTranslations };
}

// Make available globally
window.i18n = {
    t,
    setLanguage,
    getLanguage,
    getAvailableLanguages,
    createLanguageSwitcher,
    applyTranslations,
    loadTranslations,
    get translations() { return translations; }
};
