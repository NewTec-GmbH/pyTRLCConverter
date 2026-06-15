(function () {
    /**
     * Loads a JavaScript file dynamically.
     *
     * @param {string} url - Absolute or relative URL of the script to load.
     * @returns {Promise<boolean>} Resolves to true when the script is loaded.
     */
    function loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.async = true;
            script.onload = () => resolve(true);
            script.onerror = () => reject(new Error(`Failed to load ${url}`));
            document.head.appendChild(script);
        });
    }

    /**
     * Builds candidate URLs for selector data.
     *
     * @returns {{ shared: string, local: string }}
     * Object containing the shared selector data URL and local fallback URL.
     */
    function getSelectorDataUrls() {
        if (document.currentScript && document.currentScript.src) {
            const scriptUrl = new URL(document.currentScript.src, window.location.href);
            return {
                shared: new URL('./../versions/version_selector_data.js', scriptUrl).toString(),
                local: new URL('version_selector_data.js', scriptUrl).toString()
            };
        }

        return {
            shared: new URL('./../versions/version_selector_data.js', window.location.href).toString(),
            local: new URL('./_static/version_selector_data.js', window.location.href).toString()
        };
    }

    /**
     * Ensures selector data is available on the window object.
     *
     * Attempts to load shared data first and falls back to local data.
     *
     * @returns {Promise<void>} Resolves when loading attempts complete.
     */
    async function ensureSelectorData() {
        const selectorData = window.PYTRLC_DOCS_VERSION_SELECTOR;
        if (selectorData && Array.isArray(selectorData.versions)) {
            return;
        }

        const urls = getSelectorDataUrls();

        try {
            await loadScript(urls.shared);
            return;
        } catch (error) {
            // Fallback to version-local data when the shared file is not available.
        }

        try {
            await loadScript(urls.local);
        } catch (error) {
            // Keep silent: selector is optional when no data file is available.
        }
    }

    /**
     * Injects the version selector into the sidebar when data and container exist.
     *
     * @returns {boolean}
     * True when no further retry is needed (injected, already present, or no data),
     * false when the sidebar is not yet available and a retry should be attempted.
     */
    function injectVersionSelector() {
        const selectorData = window.PYTRLC_DOCS_VERSION_SELECTOR;
        if (!selectorData || !Array.isArray(selectorData.versions) || selectorData.versions.length === 0) {
            return true;
        }

        if (document.getElementById('local-version-select')) {
            return true;
        }

        const sidebar = document.querySelector('.wy-side-nav-search');
        if (!sidebar) {
            return false;
        }

        const wrapper = document.createElement('div');
        wrapper.className = 'local-version-selector';

        const label = document.createElement('label');
        label.setAttribute('for', 'local-version-select');
        label.textContent = 'Version';

        const select = document.createElement('select');
        select.id = 'local-version-select';

        selectorData.versions.forEach((versionEntry) => {
            const option = document.createElement('option');
            option.value = versionEntry.url;
            option.textContent = versionEntry.label;
            if (versionEntry.label === selectorData.current) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        select.addEventListener('change', () => {
            if (select.value) {
                window.location.href = select.value;
            }
        });

        wrapper.appendChild(label);
        wrapper.appendChild(select);
        sidebar.appendChild(wrapper);
        return true;
    }

    /**
     * Starts selector injection and retries briefly until sidebar markup exists.
     *
     * @returns {void}
     */
    function startInjectionWithRetry() {
        if (injectVersionSelector()) {
            return;
        }

        let attemptsLeft = 20;
        const timer = window.setInterval(() => {
            attemptsLeft -= 1;
            if (injectVersionSelector() || attemptsLeft <= 0) {
                window.clearInterval(timer);
            }
        }, 100);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            ensureSelectorData().then(startInjectionWithRetry);
        });
    } else {
        ensureSelectorData().then(startInjectionWithRetry);
    }
})();
