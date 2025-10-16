document.addEventListener("DOMContentLoaded", function() {
    const defaultOptions = {
        buttonColor: '#62733d',
        buttonIconColor: '#a68932',
        highlightColor: '#a68932',
        menuBackgroundColor: '#262626',
        menuTextColor: '#ffffff',
        customLabels: {}
    };

    const userOptions = window.siennaOptions || {};
    const options = { ...defaultOptions, ...userOptions };

    let t = { states: {} };
    // Speech synthesis state for "read page" feature
    let _aswSpeech = { utter: null, isReading: false };

    // Initialize speech synthesis on first user interaction
    function initSpeechSynthesis() {
        if (!_aswSpeech.initialized && 'speechSynthesis' in window) {
            // Force Chrome to load voices
            window.speechSynthesis.getVoices();
            // Cancel any pending speech to reset state
            window.speechSynthesis.cancel();
            _aswSpeech.initialized = true;
        }
    }

    const e = function() {
        !function(t, e, s) {
            const a = new Date;
            a.setTime(a.getTime() + NaN);
            let n = "expires=" + a.toUTCString();
            document.cookie = "asw=" + e + ";" + n + ";path=/"
        }(0, JSON.stringify(t))
    };
    let s = function(t) {
        let e = "asw=", s = decodeURIComponent(document.cookie).split(";");
        for (let t = 0; t < s.length; t++) {
            let a = s[t];
            for (; " " == a.charAt(0);) a = a.substring(1);
            if (0 == a.indexOf(e)) return a.substring(e.length, a.length)
        }
        return ""
    }();
    try {
        s = JSON.parse(s)
    } catch (t) {}
    t = { states: {}, ...s };
    let a = ["format_size", "add", "remove", "restart_alt", "close"];
    const n = function(e, s) {
        let n = "";
        for (var i = e.length; i--;) {
            let o = e[i], l = t.states[o.key];
            "asw-filter" == s && t.states.contrast == o.key && (l = !0);
            const label = options.customLabels[o.label] || o.label;
            n += `\n<div class="asw-btn ${s || ""} ${l ? "asw-selected" : ""}" role="button" aria-pressed="false" data-key="${o.key}" aria-label="${label}" title="${label}"><span class="material-icons">${o.icon}</span>${label}\n</div>`;
            a.push(o.icon)
        }
        return n
    };
    let i = n([
            { label: "Readable Font", key: "readable-font", icon: "local_parking" },
            { label: "Highlight Links", key: "highlight-links", icon: "link" },
        { label: "Highlight Title", key: "highlight-title", icon: "title" },
        { label: "Read Page", key: "read-page", icon: "record_voice_over" },
        { label: "Read Full Page", key: "read-full", icon: "subscriptions" }
        ]),
        o = n([
            { label: "Monochrome", key: "monochrome", icon: "filter_b_and_w" },
            { label: "Low Saturation", key: "low-saturation", icon: "gradient" },
            { label: "High Saturation", key: "high-saturation", icon: "filter_vintage" },
            { label: "High Contrast", key: "high-contrast", icon: "tonality" },
            { label: "Light Contrast", key: "light-contrast", icon: "brightness_5" },
            { label: "Dark Contrast", key: "dark-contrast", icon: "nightlight" }
        ], "asw-filter"),
        l = n([
            { label: "Big Cursor", key: "big-cursor", icon: "mouse" },
            { label: "Stop Animations", key: "stop-animations", icon: "motion_photos_off" },
            { label: "Reading Guide", key: "readable-guide", icon: "local_library" }
        ], "asw-tools");
    var r = document.createElement("div");
    r.innerHTML = `
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons&text=${a.toString()}" rel="stylesheet">
    <style>
        .asw-menu, .asw-menu-btn { position: fixed; left: 20px; transition: .3s; z-index: 500000; }
        .asw-widget { -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; font-weight: 400; -webkit-font-smoothing: antialiased; }
        .asw-widget * { box-sizing: border-box; }
        .asw-menu-btn { bottom: 20px; background: ${options.buttonColor}; box-shadow: 0 5px 15px 0 rgb(37 44 97 / 15%), 0 2px 4px 0 rgb(93 100 148 / 20%); border-radius: 50%; align-items: center; justify-content: center; transform: translateY(0); width: 50px; height: 50px; display: flex; fill: ${options.buttonIconColor} !important; cursor: pointer; }
        .asw-menu-btn svg { width: 30px; height: 30px; min-height: 30px; min-width: 30px; max-width: 30px; max-height: 30px; background: 0 0 !important; }
        .asw-menu-btn:hover { transform: scale(1.05); }
        .asw-menu { display: none; top: 20px; border-radius: 8px; box-shadow: -1px 0 20px -14px #000; opacity: 1; overflow: hidden; background: ${options.menuBackgroundColor}; width: 500px; line-height: 1; font-size: 14px; height: calc(100vh - 40px - 75px); letter-spacing: .015em; color: ${options.menuTextColor}; }
        .asw-btn, .asw-footer a { font-size: 14px !important; }
        .asw-menu-header { display: flex; align-items: center; justify-content: space-between; background: #62733d; color: #fff; padding-left: 12px; font-weight: 600; }
        .asw-menu-header > div { display: flex; }
        .asw-menu-header div[role=button] { padding: 12px; cursor: pointer; }
        .asw-menu-header div[role=button]:hover, .asw-minus:hover, .asw-plus:hover { opacity: .8; }
        .asw-items { display: flex; gap: 10px; padding: 0; list-style: none; flex-wrap: wrap; justify-content: space-between; }
        .asw-btn { width: 140px; height: 120px; border-radius: 8px; padding: 15px; display: flex; align-items: center; justify-content: center; flex-direction: column; text-align: center; color: #fff; background: #3a3a3a; border: 3px solid #3a3a3a; transition: background-color .3s; cursor: pointer; }
        .asw-btn .material-icons { margin-bottom: 16px; }
        .asw-btn:hover { border-color: ${options.highlightColor}; }
        .asw-btn.asw-selected { background: ${options.highlightColor}; color: #fff; border-color: ${options.highlightColor}; }
        .asw-footer { position: absolute; bottom: 0; left: 0; right: 0; background: #62733d; padding: 16px; text-align: center; color: #fff; }
        .asw-footer a { text-decoration: underline; color: #fff; background: 0 0 !important; }
        .asw-menu-content { overflow: scroll; max-height: calc(100% - 80px); }
        .asw-card { margin: 0 15px 30px; }
        .asw-card-title { font-size: 18px; padding: 15px 0; color: #fff; }
        .asw-adjust-font { background: #3a3a3a; padding: 20px 25px; margin-bottom: 16px; color: #fff; }
        .asw-adjust-font .label { display: flex; align-items: center; }
        .asw-adjust-font > div { display: flex; justify-content: space-between; margin-top: 20px; align-items: center; font-size: 16px; font-weight: 700; }
        .asw-adjust-font div[role=button] { background: #a68932; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer; }
        .asw-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 10000; display: none; }
        @media only screen and (max-width: 560px) {
            .asw-menu { width: calc(100vw - 20px); left: 10px; }
            .asw-btn { width: calc(50% - 8px); }
        }
    </style>
    <div class="asw-widget">
        <div class="asw-menu-btn" title="Open Accessibility Menu" role="button" aria-expanded="false">
            <svg xmlns="http://www.w3.org/2000/svg" style="width:34px;height:34px;min-height:34px;min-width:34px;max-width:34px;max-height:34px;" viewBox="0 0 24 24" width="34px" height="34px">
                <path d="M0 0h24v24H0V0z" fill="none"/>
                <path d="M20.5 6c-2.61.7-5.67 1-8.5 1s-5.89-.3-8.5-1L3 8c1.86.5 4 .83 6 1v13h2v-6h2v6h2V9c2-.17 4.14-.5 6-1l-.5-2zM12 6c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/>
            </svg>
        </div>
        <div class="asw-menu">
            <div class="asw-menu-header">Accesibilidad
                <div>
                    <div role="button" class="asw-menu-reset" title="Reset Settings">
                        <span class="material-icons">reiniciar</span>
                    </div>
                    <div role="button" class="asw-menu-close" title="Close Accessibility Menu">
                        <span class="material-icons">cerrar</span>
                    </div>
                </div>
            </div>
            <div class="asw-menu-content">
                <div class="asw-card" style="margin-top: 15px;">
                    <div class="asw-card-title">Ajustes</div>
                    <div class="asw-adjust-font">
                        <div class="label">
                            <span class="material-icons" style="margin-right:8px;">format_size</span> Tamaño de Fuente
                        </div>
                        <div>
                            <div class="asw-minus" data-key="font-size" role="button" aria-pressed="false">
                                <span class="material-icons">remove</span>
                            </div>
                            <div class="asw-amount">${t.states.fontSize && 1 != t.states.fontSize ? `${parseInt(100 * t.states.fontSize)}%` : "Normal"}</div>
                            <div class="asw-plus" data-key="font-size" role="button" aria-pressed="false">
                                <span class="material-icons">add</span>
                            </div>
                        </div>
                    </div>
                    <div class="asw-items">${i}</div>
                </div>
                <div class="asw-card" style="margin-top: 15px;">
                    <div class="asw-card-title">Ajustes de Color</div>
                    <div class="asw-items">${o}</div>
                </div>
                <div class="asw-card" style="margin-top: 15px;">
                    <div class="asw-card-title">Herramientas</div>
                    <div class="asw-items">${l}</div>
                </div>
            </div>
            <div class="asw-footer">
                <a href="https://bennyluk.github.io/Sienna-Accessibility-Widget/">By: Sienna Free Accessibility Widget</a>
            </div>
        </div>
        <div class="asw-overlay"></div>
    </div>`;
    const c = function(t, e) {
        let s = document.getElementById(e || "") || document.createElement("style");
        s.innerHTML = t, s.id || (s.id = e, document.head.appendChild(s))
    }, d = function(t, e) {
        let s = "", a = ["-o-", "-ms-", "-moz-", "-webkit", ""];
        for (var n = a.length; n--;) s += a[n] + (e || "filter") + ":" + t + ";";
        return s
    }, p = function(t) {
        let e = "";
        if (t) {
            let a = "";
            "dark-contrast" == t ? a = "color: #fff !important;fill: #FFF !important;background-color: #000 !important;" : "light-contrast" == t ? a = " color: #000 !important;fill: #000 !important;background-color: #FFF !important;" : "high-contrast" == t ? a += d("contrast(125%)") : "high-saturation" == t ? a += d("saturate(200%)") : "low-saturation" == t ? a += d("saturate(50%)") : "monochrome" == t && (a += d("grayscale(100%)"));
            let n = [""];
            "dark-contrast" != t && "light-contrast" != t || (n = ["h1", "h2", "h3", "h4", "h5", "h6", "img", "p", "i", "svg", "a", "button", "label", "li", "ol"]);
            for (var s = n.length; s--;) e += '[data-asw-filter="' + t + '"] ' + n[s] + "{" + a + "}"
        }
        c(e, "asw-filter-style"), t ? document.documentElement.setAttribute("data-asw-filter", t) : document.documentElement.removeAttribute("data-asw-filter", t)
    }, u = function() {
        let e = [{
            id: "highlight-title",
            childrenSelector: ["h1", "h2", "h3", "h4", "h5", "h6"],
            css: "outline: 2px solid " + options.highlightColor + " !important;outline-offset: 2px !important;"
        }, {
            id: "highlight-links",
            childrenSelector: ["a[href]"],
            css: "outline: 2px solid " + options.highlightColor + " !important;outline-offset: 2px !important;"
        }, {
            id: "readable-font",
            childrenSelector: ["", "h1", "h2", "h3", "h4", "h5", "h6", "img", "p", "i", "svg", "a", "button", "label", "li", "ol"],
            css: "font-family: OpenDyslexic3,Comic Sans MS,Arial,Helvetica,sans-serif !important;"
        }], s = "";
        for (var a = e.length; a--;) {
            let i = e[a];
            if (document.documentElement.classList.toggle(i.id, !!t.states[i.id]), t.states[i.id]) for (var n = i.childrenSelector.length; n--;) s += "." + i.id + " " + i.childrenSelector[n] + "{" + i.css + "}"
        }
        var i = document.querySelector(".asw-rg-container");
        if (t.states["readable-guide"]) {
            if (!i) {
                var o = document.createElement("div");
                o.setAttribute("class", "asw-rg-container"), o.innerHTML = '<style>    .asw-rg {position: fixed;top: 0;left: 0;right: 0;width: 100%;height: 0;pointer-events: none;background-color: rgba(0,0,0,.5);z-index: 1000000;    }</style><div class="asw-rg asw-rg-top"></div><div class="asw-rg asw-rg-bottom" style="top: auto;bottom: 0;"></div>\n';
                let t = o.querySelector(".asw-rg-top"), e = o.querySelector(".asw-rg-bottom"), s = 20;
                window.onScrollReadableGuide = function(a) {
                    t.style.height = a.clientY - s + "px", e.style.height = window.innerHeight - a.clientY - s - s + "px"
                }, document.addEventListener("mousemove", window.onScrollReadableGuide, !1), document.body.appendChild(o)
            }
        } else i && (i.remove(), document.removeEventListener("mousemove", window.onScrollReadableGuide));
        t.states["stop-animations"] && (s += `\nbody * {${d("none !important", "transition")}${d("forwards !important", "animation-fill-mode")}${d("1 !important", " animation-iteration-count")}${d(".01s !important", "animation-duration")}\n}`), t.states["big-cursor"] && (s += "\nbody * {cursor: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 512 512'%3E%3Cpath  d='M429.742 319.31L82.49 0l-.231 471.744 105.375-100.826 61.89 141.083 96.559-42.358-61.89-141.083 145.549-9.25zM306.563 454.222l-41.62 18.259-67.066-152.879-85.589 81.894.164-333.193 245.264 225.529-118.219 7.512 67.066 152.878z' xmlns='http://www.w3.org/2000/svg'/%3E%3C/svg%3E\") ,default !important;\n}"), t.states["readable-font"] && (s += '\n@font-face {font-family: OpenDyslexic3;src: url("https://website-widgets.pages.dev/fonts/OpenDyslexic3-Regular.woff") format("woff"), url("https://website-widgets.pages.dev/fonts/OpenDyslexic3-Regular.ttf") format("truetype");\n}'), c(s, "asw-content-style")
    };
    var f = function(s) {
        s.preventDefault();
        let a = s.currentTarget, n = a.dataset.key;
        // Special handling for filters
        if (a.classList.contains("asw-filter")) {
            document.querySelectorAll(".asw-filter").forEach((function(t) {
                t.classList.remove("asw-selected"), t.setAttribute("aria-pressed", "false")
            }));
            t.states.contrast = t.states.contrast !== n && n;
            if (t.states.contrast) { a.classList.add("asw-selected"); a.setAttribute("aria-pressed", "true") }
            p(t.states.contrast);
        } else if (n === "read-page") {
            // Toggle cursor-read mode (reads element under mouse)
            // Initialize speech synthesis first
            initSpeechSynthesis();

            if (_aswSpeech.mode !== 'cursor') {
                t.states['read-page'] = true;
                enableCursorMode();
                a.classList.add('asw-selected');
                a.setAttribute('aria-pressed', 'true');
                // announce to user briefly with delay to allow initialization
                setTimeout(function() {
                    try {
                        if ('speechSynthesis' in window) {
                            // Cancel any pending speech first
                            window.speechSynthesis.cancel();

                            const ann = new SpeechSynthesisUtterance('Modo lectura por cursor activado. Mueva el cursor sobre el texto para escuchar.');
                            ann.lang = document.documentElement.lang || 'es-ES';
                            ann.rate = 1;
                            ann.pitch = 1;
                            ann.volume = 1;

                            window.speechSynthesis.speak(ann);
                        }
                    } catch (e) {}
                }, 100);
            } else {
                t.states['read-page'] = false;
                disableCursorMode();
                a.classList.remove('asw-selected');
                a.setAttribute('aria-pressed', 'false');
            }
        } else if (n === 'read-full') {
            // Toggle or start full-page reading

            // Initialize speech synthesis first
            initSpeechSynthesis();

            if (_aswSpeech.mode === 'full' && _aswSpeech.isReading) {
                // Stop reading if already active
                t.states['read-full'] = false;
                stopFullReading();
                a.classList.remove('asw-selected');
                a.setAttribute('aria-pressed', 'false');
            } else {
                // Announce then start full-page reading
                t.states['read-full'] = true;
                a.classList.add('asw-selected');
                a.setAttribute('aria-pressed', 'true');

                setTimeout(function() {
                    try {
                        if ('speechSynthesis' in window) {
                            // Cancel any pending speech first
                            window.speechSynthesis.cancel();

                            const announcement = 'Se va a leer toda la página. Para pausar o reanudar presione la barra espaciadora. Para retroceder o avanzar use las flechas izquierda y derecha. Para cancelar presione Escape.';
                            const utt = new SpeechSynthesisUtterance(announcement);
                            utt.lang = document.documentElement.lang || 'es-ES';
                            utt.rate = 1;
                            utt.pitch = 1;
                            utt.volume = 1;
                            utt.onend = function() {
                                startFullReading();
                            };
                            utt.onerror = function(e) {
                                // Start reading anyway even if announcement fails
                                startFullReading();
                            };
                            window.speechSynthesis.speak(utt);
                        } else {
                            // fallback: start immediately
                            startFullReading();
                        }
                    } catch (e) {
                        startFullReading();
                    }
                }, 100);
            }
        } else {
            t.states[n] = !t.states[n];
            a.classList.toggle("asw-selected", t.states[n]);
            a.setAttribute("aria-pressed", t.states[n] ? "true" : "false");
            u();
        }
        e();
    };

    // Collect visible text from the document excluding the widget
    function collectPageText() {
        // Get text from block-level elements to preserve structure
        const elements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, div, article, section');
        let text = '';

        for (let el of elements) {
            // Skip widget elements
            if (el.closest('.asw-widget') || el.closest('.asw-menu')) continue;

            // Skip elements inside other already processed elements (avoid duplicates)
            let isNested = false;
            for (let parent of elements) {
                if (parent !== el && parent.contains(el)) {
                    isNested = true;
                    break;
                }
            }
            if (isNested) continue;

            // Get direct text content
            const elementText = (el.innerText || el.textContent || '').trim();
            if (elementText && elementText.length > 2) {
                // Add double space as separator to help with splitting
                text += elementText + '  ';
            }
        }

        return text.trim();
    }

    // Read-mode: supports cursor mode (reads element under cursor) and full-page mode with keyboard controls

    function enableCursorMode() {
        // remove any full-reading state
        stopAllSpeech();
        removeKeyboardControls();
        _aswSpeech.mode = 'cursor';

        // Remove old handler if exists to avoid duplicates
        if (_aswSpeech.mouseHandler) {
            document.removeEventListener('mousemove', _aswSpeech.mouseHandler, false);
        }

        _aswSpeech.mouseHandler = function(ev) {
            if (_aswSpeech.mode !== 'cursor') return;
            if (_aswSpeech.debounceTimer) clearTimeout(_aswSpeech.debounceTimer);
            _aswSpeech.debounceTimer = setTimeout(function() {
                // Get target element (handle text nodes)
                let target = ev.target;
                if (target.nodeType === 3) target = target.parentElement; // text node
                if (!target) return;

                // Check if it's inside the accessibility widget
                const isInWidget = target.closest('.asw-widget') || target.closest('.asw-menu');

                // For widget buttons, read their aria-label or title or text
                if (isInWidget) {
                    // Check if it's a button or has role="button"
                    let btnElement = target;
                    if (!btnElement.hasAttribute('role') && btnElement.tagName !== 'BUTTON') {
                        btnElement = target.closest('[role="button"], .asw-btn, button');
                    }

                    if (btnElement) {
                        const btnLabel = btnElement.getAttribute('aria-label') ||
                                       btnElement.getAttribute('title') ||
                                       (btnElement.innerText || btnElement.textContent || '').trim();
                        if (btnLabel && btnLabel.length > 0) {
                            speakTextSegment(btnLabel);
                            return;
                        }
                    }

                    // If it's other widget content, read it
                    const widgetText = (target.innerText || target.textContent || '').trim();
                    if (widgetText && widgetText.length > 2) {
                        speakTextSegment(widgetText);
                        return;
                    }

                    // Don't read if nothing found in widget
                    return;
                }

                // Check if element has a title attribute (tooltip)
                const titleAttr = target.getAttribute('title');
                if (titleAttr && titleAttr.trim()) {
                    speakTextSegment(titleAttr.trim());
                    return;
                }

                // Check if it's an image and read alt text
                if (target.tagName && target.tagName.toUpperCase() === 'IMG') {
                    const altText = target.getAttribute('alt') || 'Imagen sin descripción';
                    if (altText && altText.trim()) {
                        speakTextSegment('Imagen: ' + altText.trim());
                        return;
                    }
                }

                // Check if it's a link and has aria-label
                const ariaLabel = target.getAttribute('aria-label');
                if (ariaLabel && ariaLabel.trim()) {
                    speakTextSegment(ariaLabel.trim());
                    return;
                }

                // Find nearest readable element
                let el = target;
                if (target.matches && !target.matches('p,h1,h2,h3,h4,h5,h6,li,a,span,div,section,article,main,header,footer,img,button')) {
                    el = target.closest('p,h1,h2,h3,h4,h5,h6,li,a,span,div,section,article,main,header,footer,img,button');
                }
                if (!el) return;

                // Check again if the closest element has title
                const elTitle = el.getAttribute('title');
                if (elTitle && elTitle.trim()) {
                    speakTextSegment(elTitle.trim());
                    return;
                }

                // Check again if the closest element is an image
                if (el.tagName && el.tagName.toUpperCase() === 'IMG') {
                    const altText = el.getAttribute('alt') || 'Imagen sin descripción';
                    if (altText && altText.trim()) {
                        speakTextSegment('Imagen: ' + altText.trim());
                        return;
                    }
                }

                // For buttons, read their text or aria-label
                if (el.tagName && el.tagName.toUpperCase() === 'BUTTON') {
                    const btnText = el.getAttribute('aria-label') || el.getAttribute('title') || (el.innerText || el.textContent || '').trim();
                    if (btnText && btnText.length > 0) {
                        speakTextSegment('Botón: ' + btnText);
                        return;
                    }
                }

                // Avoid reading input/textarea/select
                if (el.tagName && ['INPUT','TEXTAREA','SELECT'].includes(el.tagName.toUpperCase())) return;

                const text = (el.innerText || el.textContent || '').trim();
                if (!text || text.length < 3) return; // skip very short texts

                speakTextSegment(text);
            }, 350);
        };
        document.addEventListener('mousemove', _aswSpeech.mouseHandler, false);
    }

    function disableCursorMode() {
        if (_aswSpeech.mouseHandler) {
            document.removeEventListener('mousemove', _aswSpeech.mouseHandler, false);
            _aswSpeech.mouseHandler = null;
        }
        if (_aswSpeech.debounceTimer) clearTimeout(_aswSpeech.debounceTimer);
        stopAllSpeech();
        _aswSpeech.mode = null;
    }

    function speakTextSegment(text) {
        if (!('speechSynthesis' in window)) return;
        stopAllSpeech();

        // Small delay to ensure speech engine is ready
        setTimeout(function() {
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(text);
            u.rate = 1;
            u.pitch = 1;
            u.volume = 1;
            u.lang = document.documentElement.lang || 'es-ES';
            u.onend = function() { _aswSpeech.isReading = false; };
            _aswSpeech.utter = u;
            _aswSpeech.isReading = true;
            window.speechSynthesis.speak(u);
        }, 50);
    }    function startFullReading() {
        if (!('speechSynthesis' in window)) return;
        removeKeyboardControls();
        _aswSpeech.fullText = collectPageText();
        if (!_aswSpeech.fullText) return;

        // Split text into sentences for more precise pause/resume
        _aswSpeech.sentences = splitIntoSentences(_aswSpeech.fullText);
        _aswSpeech.sentenceIndex = 0;
        _aswSpeech.paused = false;
        _aswSpeech.mode = 'full';
        addKeyboardControls();
        speakNextSentence();
    }

    function splitIntoSentences(text) {
        // First, split by common sentence delimiters and line breaks
        // This regex splits on: . ! ? or 2+ spaces or line-like breaks
        const rawSegments = text.split(/([.!?]+\s+|\s{2,})/);

        const segments = [];
        let current = '';

        for (let i = 0; i < rawSegments.length; i++) {
            const segment = rawSegments[i];
            if (!segment || /^\s*$/.test(segment)) continue;

            // Check if it's a delimiter
            if (/^[.!?]+\s+$/.test(segment)) {
                if (current) {
                    segments.push(current.trim());
                    current = '';
                }
                continue;
            }

            current += segment;

            // If current segment is long enough or ends with punctuation, push it
            if (current.length > 80 || /[.!?]\s*$/.test(current)) {
                segments.push(current.trim());
                current = '';
            }
        }

        if (current.trim()) {
            segments.push(current.trim());
        }

        // Further split any segment that's still too long (> 200 chars)
        const finalSegments = [];
        for (let segment of segments) {
            if (segment.length <= 200) {
                finalSegments.push(segment);
            } else {
                // Split long segments by words, keeping ~100 chars per chunk
                const words = segment.split(/\s+/);
                let chunk = '';
                for (let word of words) {
                    if (chunk.length + word.length + 1 > 120 && chunk.length > 0) {
                        finalSegments.push(chunk.trim());
                        chunk = word;
                    } else {
                        chunk += (chunk ? ' ' : '') + word;
                    }
                }
                if (chunk.trim()) {
                    finalSegments.push(chunk.trim());
                }
            }
        }

        return finalSegments.filter(s => s.length > 0);
    }

    function speakNextSentence() {
        if (!_aswSpeech.sentences || _aswSpeech.sentences.length === 0) return;
        if (_aswSpeech.paused) return; // Don't start new sentence if paused
        if (_aswSpeech.sentenceIndex >= _aswSpeech.sentences.length) {
            // Finished reading entire page
            stopFullReading();
            return;
        }

        const sentence = _aswSpeech.sentences[_aswSpeech.sentenceIndex];

        // Cancel any previous speech
        if (window.speechSynthesis && window.speechSynthesis.speaking && !_aswSpeech.paused) {
            window.speechSynthesis.cancel();
        }

        // Small delay to ensure speech engine is ready
        setTimeout(function() {
            const u = new SpeechSynthesisUtterance(sentence);
            u.rate = 1;
            u.pitch = 1;
            u.volume = 1;
            u.lang = document.documentElement.lang || 'es-ES';

            // Track character position for pause/resume functionality
            _aswSpeech.lastCharIndex = 0;
            u.onboundary = function(event) {
                if (event.name === 'word' || event.name === 'sentence') {
                    _aswSpeech.lastCharIndex = event.charIndex;
                }
            };

            u.onend = function() {
                if (_aswSpeech.paused) return; // Don't advance if paused
                _aswSpeech.sentenceIndex++;
                _aswSpeech.lastCharIndex = 0; // Reset for next sentence
                // Small delay then next sentence
                setTimeout(function() { speakNextSentence(); }, 50);
            };

            u.onerror = function(e) {
                // Only continue if error is not 'interrupted' and not paused
                if (e.error === 'interrupted') {
                    // Speech was intentionally interrupted, don't retry
                    return;
                }
                // For other errors, try to continue with next sentence
                if (!_aswSpeech.paused && _aswSpeech.mode === 'full') {
                    _aswSpeech.sentenceIndex++;
                    setTimeout(function() { speakNextSentence(); }, 100);
                }
            };

            _aswSpeech.utter = u;
            _aswSpeech.isReading = true;
            window.speechSynthesis.speak(u);
        }, 50);
    }

    function stopFullReading() {
        stopAllSpeech();
        removeKeyboardControls();
        _aswSpeech.mode = null;
        _aswSpeech.fullText = null;
        _aswSpeech.sentences = null;
        _aswSpeech.sentenceIndex = 0;
        _aswSpeech.paused = false; // Reset paused state
        // Remove blue highlight from button
        const btn = document.querySelector('[data-key="read-full"]');
        if (btn) {
            btn.classList.remove('asw-selected');
            btn.setAttribute('aria-pressed', 'false');
        }
    }

    function speakNextChunk() {
        if (!_aswSpeech.fullText) return;
        if (_aswSpeech.paused) return; // Don't start new chunk if paused
        if (_aswSpeech.index >= _aswSpeech.fullText.length) {
            // Finished reading entire page
            stopFullReading();
            return;
        }
        const remaining = _aswSpeech.fullText.length - _aswSpeech.index;
        const size = Math.min(_aswSpeech.chunkSize, remaining);
        const chunk = _aswSpeech.fullText.substr(_aswSpeech.index, size);

        // Only cancel if not paused (to avoid conflicts)
        if (window.speechSynthesis && window.speechSynthesis.speaking && !_aswSpeech.paused) {
            window.speechSynthesis.cancel();
        }

        const u = new SpeechSynthesisUtterance(chunk);
        u.rate = 1; u.pitch = 1; u.lang = document.documentElement.lang || 'es-ES';
        u.onend = function() {
            if (_aswSpeech.paused) return; // Don't advance if paused
            _aswSpeech.index += size;
            // small delay then next
            setTimeout(function() { speakNextChunk(); }, 120);
        };
        _aswSpeech.utter = u;
        _aswSpeech.isReading = true;
        _aswSpeech.currentChunkSize = size; // Save current chunk size for pause/resume
        window.speechSynthesis.speak(u);
    }

    function pauseFullReading() {
        _aswSpeech.paused = true;
        _aswSpeech.isReading = false;
        // Cancel current speech and save the current position
        if (window.speechSynthesis && window.speechSynthesis.speaking) {
            // Save the current sentence and character position before canceling
            _aswSpeech.pausedSentenceIndex = _aswSpeech.sentenceIndex;
            _aswSpeech.pausedCharIndex = _aswSpeech.lastCharIndex || 0;
            window.speechSynthesis.cancel();
        }
    }

    function resumeFullReading() {
        if (!_aswSpeech.sentences || _aswSpeech.sentences.length === 0) return;
        _aswSpeech.paused = false;

        // Resume from the saved position within the sentence
        if (_aswSpeech.pausedCharIndex && _aswSpeech.pausedCharIndex > 0) {
            const currentSentence = _aswSpeech.sentences[_aswSpeech.sentenceIndex];
            // Resume from the saved character position
            const remainingText = currentSentence.substring(_aswSpeech.pausedCharIndex);

            if (remainingText && remainingText.trim().length > 0) {
                const u = new SpeechSynthesisUtterance(remainingText);
                u.rate = 1;
                u.pitch = 1;
                u.lang = document.documentElement.lang || 'es-ES';

                // Track character position
                u.onboundary = function(event) {
                    if (event.name === 'word' || event.name === 'sentence') {
                        _aswSpeech.lastCharIndex = _aswSpeech.pausedCharIndex + event.charIndex;
                    }
                };

                u.onend = function() {
                    if (_aswSpeech.paused) return;
                    _aswSpeech.sentenceIndex++;
                    _aswSpeech.lastCharIndex = 0;
                    _aswSpeech.pausedCharIndex = 0;
                    setTimeout(function() { speakNextSentence(); }, 50);
                };

                _aswSpeech.utter = u;
                _aswSpeech.isReading = true;
                _aswSpeech.pausedCharIndex = 0; // Clear paused position
                window.speechSynthesis.speak(u);
            } else {
                // If nothing remains in current sentence, move to next
                _aswSpeech.sentenceIndex++;
                _aswSpeech.pausedCharIndex = 0;
                speakNextSentence();
            }
        } else {
            // Continue from current sentence index (from the beginning)
            speakNextSentence();
        }
    }

    function stopAllSpeech() {
        try {
            if (window.speechSynthesis && window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
            }
        } catch (e) {}
        _aswSpeech.utter = null;
        _aswSpeech.isReading = false;
        // Don't reset paused here - let other functions control it
    }

    function addKeyboardControls() {
        _aswSpeech.keyboardHandler = function(ev) {
            if (!_aswSpeech.sentences || _aswSpeech.sentences.length === 0) return;
            if (ev.code === 'Space') {
                ev.preventDefault();
                if (_aswSpeech.paused || !_aswSpeech.isReading) {
                    resumeFullReading();
                } else {
                    pauseFullReading();
                }
            } else if (ev.code === 'ArrowLeft') {
                ev.preventDefault();
                // Cancel current speech first
                window.speechSynthesis.cancel();
                // Go back one sentence
                _aswSpeech.sentenceIndex = Math.max(0, _aswSpeech.sentenceIndex - 1);
                _aswSpeech.paused = false;
                // Wait a bit before speaking to avoid interruption errors
                setTimeout(function() {
                    speakNextSentence();
                }, 150);
            } else if (ev.code === 'ArrowRight') {
                ev.preventDefault();
                // Cancel current speech first
                window.speechSynthesis.cancel();
                // Go forward one sentence
                _aswSpeech.sentenceIndex = Math.min(_aswSpeech.sentences.length - 1, _aswSpeech.sentenceIndex + 1);
                _aswSpeech.paused = false;
                // Wait a bit before speaking to avoid interruption errors
                setTimeout(function() {
                    speakNextSentence();
                }, 150);
            } else if (ev.code === 'Escape') {
                ev.preventDefault();
                // Cancel reading completely
                stopFullReading();
            }
        };
        document.addEventListener('keydown', _aswSpeech.keyboardHandler, false);
    }

    function removeKeyboardControls() {
        if (_aswSpeech.keyboardHandler) {
            document.removeEventListener('keydown', _aswSpeech.keyboardHandler, false);
            _aswSpeech.keyboardHandler = null;
        }
    }
    const h = function(e, s) {
        let a = !1;
        !s && e && (a = e.currentTarget, s = parseFloat(t.states.fontSize) || 1, a.classList.contains("asw-minus") ? s -= .1 : s += .1, s = Math.max(s, .1), s = Math.min(s, 2), s = parseFloat(s.toFixed(2))), document.querySelectorAll("h1,h2,h3,h4,h5,h6,p,a,dl,dt,li,ol,th,td,span").forEach((function(t) {
            if (!t.classList.contains("material-icons")) {
                let e = t.getAttribute("data-asw-orgFontSize");
                e || (e = parseInt(window.getComputedStyle(t, null).getPropertyValue("font-size")), t.setAttribute("data-asw-orgFontSize", e));
                let a = e * s;
                t.style["font-size"] = a + "px"
            }
        }));
        let n = "Default";
        1 !== s && (s > 1 ? n = "+" : s < 1 && (n = "-"), n += parseInt(100 * s) + "%"), a && (a.parentElement.querySelector(".asw-amount").innerHTML = n), t.states.fontSize = s
    };
    let m = r.querySelector(".asw-menu"), g = r.querySelector(".asw-overlay");
    r.querySelector(".asw-menu-btn").addEventListener("click", function() {
        m.style.display = "block" == m.style.display ? "none" : "block", g.style.display = m.style.display
    }, !1), m.querySelector(".asw-menu-close").addEventListener("click", function() {
        m.style.display = "none", g.style.display = m.style.display
    }, !1), g.addEventListener("click", function() {
        m.style.display = "none", g.style.display = m.style.display
    }, !1), m.querySelector(".asw-menu-reset").addEventListener("click", function() {
        t.states = {}, p(), u(), h(void 0, 1), document.querySelectorAll(".asw-btn").forEach(function(t) {
            t.classList.remove("asw-selected"), t.setAttribute("aria-pressed", "false")
        }), document.querySelectorAll(".asw-amount").forEach(function(t) {
            t.innerHTML = "Default"
        }), e()
    }, !1), m.querySelectorAll(".asw-btn").forEach(function(t) {
        t.addEventListener("click", f, !1)
    }), m.querySelectorAll(".asw-adjust-font div[role='button']").forEach(function(t) {
        t.addEventListener("click", function(t) {
            h(t), e()
        }, !1)
    }), document.body.appendChild(r), s && (u(), 1 !== t.states.fontSize && h(null, t.states.fontSize), t.states.contrast && p(t.states.contrast));

    // Restore read modes if they were active
    if (t.states['read-page']) {
        initSpeechSynthesis();
        enableCursorMode();
        const readPageBtn = document.querySelector('[data-key="read-page"]');
        if (readPageBtn) {
            readPageBtn.classList.add('asw-selected');
            readPageBtn.setAttribute('aria-pressed', 'true');
        }
    }

    // Note: read-full mode is not auto-started on page load since it would be intrusive
    // But we keep the button selected to show it was active
    if (t.states['read-full']) {
        const readFullBtn = document.querySelector('[data-key="read-full"]');
        if (readFullBtn) {
            readFullBtn.classList.add('asw-selected');
            readFullBtn.setAttribute('aria-pressed', 'true');
        }
    }
});
