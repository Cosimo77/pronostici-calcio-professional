// Sistema Pronostici Serie A - JavaScript Interattivo

// Performance polyfills
if (!window.requestIdleCallback) {
    window.requestIdleCallback = function(cb, options = {}) {
        const timeout = options.timeout || 0;
        const start = Date.now();
        return setTimeout(() => {
            cb({
                didTimeout: timeout > 0 && (Date.now() - start) >= timeout,
                timeRemaining() {
                    return Math.max(0, 50 - (Date.now() - start));
                }
            });
        }, 1);
    };
}

// Performance utilities
window.debounce = function(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
};

window.throttle = function(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// Sistema semplificato senza gestione runtime browser
console.log('✅ Sistema web puro - nessun runtime browser necessario');

// Prevent extension interference and runtime.lastError
(function() {
    'use strict';
    
    // Override console.error to filter extension errors
    const originalError = console.error;
    console.error = function(...args) {
        const message = args.join(' ');
        if (message.includes('runtime.lastError') || 
            message.includes('message channel closed') ||
            message.includes('Extension context invalidated') ||
            message.includes('Unchecked runtime.lastError')) {
            return; // Silently ignore these errors
        }
        originalError.apply(console, args);
    };
    
    // Override console.warn for similar issues
    const originalWarn = console.warn;
    console.warn = function(...args) {
        const message = args.join(' ');
        if (message.includes('runtime.lastError') || 
            message.includes('message channel closed')) {
            return;
        }
        originalWarn.apply(console, args);
    };
    
    // Create a safe wrapper for chrome APIs
    if (typeof chrome !== 'undefined' && chrome.runtime) {
        const originalSendMessage = chrome.runtime.sendMessage;
        if (originalSendMessage) {
            chrome.runtime.sendMessage = function(...args) {
                try {
                    return originalSendMessage.apply(this, args);
                } catch (error) {
                    // Silently ignore extension communication errors
                    return null;
                }
            };
        }
    }
})();

class PronosticiApp {
    constructor() {
        console.log('🔧 Inizializzazione PronosticiApp ultra-leggera...');
        this.charts = {};
        this.currentSection = 'predizioni';
        this.statistiche = null;
        this.statisticsLoading = false;
        
        // Performance debounce functions - lazy init
        this.updateRaccomandazioniDebounced = null;
        
        // Inizializzazione minima istantanea
        this.initMinimal();
        
        // Defer tutto il resto usando setTimeout per non bloccare
        setTimeout(() => this.initDeferred(), 0);
        
        console.log('✅ PronosticiApp core inizializzata istantaneamente');
    }

    initMinimal() {
        // Solo status - zero DOM query
        console.log('⚡ Init minimal - zero blocking ops');
    }

    initDeferred() {
        console.log('🔄 Init deferred iniziato...');
        
        // Lazy init del debounce
        if (!this.updateRaccomandazioniDebounced) {
            this.updateRaccomandazioniDebounced = window.debounce(
                (raccomandazioni) => this.updateMercatiRaccomandazioni(raccomandazioni), 
                100
            );
        }
        
        // Inizializzazioni in microtask per non bloccare
        setTimeout(() => this.initEventListeners(), 10);
        setTimeout(() => this.initCharts(), 20);
        setTimeout(() => this.updateConnectionStatus(true), 30);
        setTimeout(() => this.initAsync(), 40);
        
        console.log('✅ Init deferred schedulato');
    }

    async initAsync() {
        try {
            // Sistema semplificato senza WebSocket
            console.log('✅ Sistema inizializzato senza WebSocket');
            
            // Statistiche lazy load ultra-ottimizzato
            if (!this.statisticsLoading && !this.statistiche) {
                this.statisticsLoading = true;
                // Use setTimeout per evitare blocking
                setTimeout(() => this.loadStatistiche(), 100);
            }
        } catch (error) {
            console.error('❌ Errore durante init async:', error);
            this.statisticsLoading = false;
        }
    }



    initEventListeners() {
        console.log('🔄 Init event listeners ottimizzato...');
        
        // Navigation - query ottimizzata
        const navLinks = document.querySelectorAll('.nav-link');
        if (navLinks.length > 0) {
            navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const section = e.target.getAttribute('data-section');
                    this.switchSection(section);
                });
            });
        }

        // Forms - query dirette per performance
        const predictionForm = document.getElementById('predizione-form');
        const mercatiForm = document.getElementById('mercati-form');
        const btnAnalizzaForma = document.getElementById('btn-analizza-forma');
        
        if (predictionForm) {
            predictionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.makePrediction();
            });
        }

        if (mercatiForm) {
            mercatiForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.makeMercatiPrediction();
            });
        }

        if (btnAnalizzaForma) {
            btnAnalizzaForma.addEventListener('click', (e) => {
                e.preventDefault();
                this.getFormaSquadra();
            });
        }

        // Reload buttons - batch query ottimizzata
        const reloadBtns = document.querySelectorAll('.reload-btn');
        if (reloadBtns.length > 0) {
            reloadBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    this.loadStatistiche();
                });
            });
        }

        // Team selection handlers - cached elements
        const squadraCasa = document.getElementById('squadra-casa');
        const squadraTrasferta = document.getElementById('squadra-trasferta');
        
        if (squadraCasa && squadraTrasferta) {
            const handleTeamChange = () => {
                const casaValue = squadraCasa.value;
                const trasfertaValue = squadraTrasferta.value;
                
                // DOM queries ottimizzate
                const resultDiv = document.getElementById('risultato-predizione');
                const mercatiDiv = document.getElementById('mercati-risultati');
                
                if (resultDiv) resultDiv.style.display = 'none';
                if (mercatiDiv) mercatiDiv.style.display = 'none';
                
                if (casaValue === trasfertaValue && casaValue) {
                    this.showAlert('Seleziona squadre diverse', 'warning');
                }
            };

            squadraCasa.addEventListener('change', handleTeamChange);
            squadraTrasferta.addEventListener('change', handleTeamChange);
        }
        
        console.log('✅ Event listeners ottimizzati inizializzati');
    }

    switchSection(sectionName) {
        console.log('🔄 Cambio sezione verso:', sectionName);
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        const sectionLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (sectionLink) {
            sectionLink.classList.add('active');
            console.log('✅ Link di navigazione aggiornato');
        }

        // Update content
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        const sectionContent = document.getElementById(sectionName);
        if (sectionContent) {
            sectionContent.classList.add('active');
            console.log('✅ Sezione visualizzata:', sectionName);
        } else {
            console.error('❌ Sezione non trovata:', sectionName);
        }

        this.currentSection = sectionName;

        // Load section-specific data
        switch(sectionName) {
            case 'statistiche':
                this.loadStatistiche();
                break;
            case 'mercati':
                // Non carica più automaticamente esempi - l'utente deve selezionare le squadre
                console.log('📊 Sezione mercati attiva - in attesa selezione squadre');
                break;
            case 'info':
                this.loadSystemInfo();
                break;
        }
    }

    async loadExampleMercati() {
        console.log('📊 Caricamento esempio mercati...');
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        
        try {
            // Carica automaticamente Inter vs Juventus come esempio
            const response = await fetch('/api/mercati', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: controller.signal,
                body: JSON.stringify({
                    squadra_casa: 'Inter',
                    squadra_ospite: 'Juventus'
                })
            });

            clearTimeout(timeoutId);
            
            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    console.log('📊 Dati mercati di esempio caricati:', data);
                    this.lastMercatiData = data;
                    this.displayMercatiResults(data);
                } else {
                    console.error('❌ Risposta non JSON per mercati di esempio:', contentType);
                }
            } else {
                console.error('❌ Errore caricamento mercati di esempio:', response.status);
            }
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name !== 'AbortError') {
                console.error('❌ Errore richiesta mercati di esempio:', error);
            }
        }
    }

    async makePrediction() {
        console.log('🔮 Inizio makePrediction...');
        
        const squadraCasa = document.getElementById('squadra-casa').value;
        const squadraOspite = document.getElementById('squadra-trasferta').value;

        console.log('🏟️ Squadre selezionate:', squadraCasa, 'vs', squadraOspite);

        if (!squadraCasa || !squadraOspite) {
            console.warn('⚠️ Squadre mancanti');
            this.showAlert('Seleziona entrambe le squadre', 'warning');
            return;
        }

        if (squadraCasa === squadraOspite) {
            console.warn('⚠️ Squadre identiche');
            this.showAlert('Seleziona squadre diverse', 'warning');
            return;
        }

        console.log('📡 Invio richiesta API...');
        this.showLoading('risultato-predizione');

        // Timeout controller per evitare richieste bloccate
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 secondi timeout

        try {
            const response = await fetch('/api/predici', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: controller.signal,
                body: JSON.stringify({
                    squadra_casa: squadraCasa,
                    squadra_ospite: squadraOspite
                })
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    console.log('📊 Risposta API ricevuta:', data);
                    console.log('✅ Risposta API OK, chiamata displayPredictionResult...');
                    this.displayPredictionResult(data);
                    // Sistema senza WebSocket - non serve emit
                } else {
                    console.error('❌ Risposta non JSON per predizioni:', contentType);
                    this.showAlert('Errore: risposta non valida dal server', 'danger');
                }
            } else {
                console.error('❌ Errore HTTP:', response.status);
                this.showAlert('Errore del server', 'danger');
            }
        } catch (error) {
            console.error('Errore:', error);
            this.showAlert('Errore di connessione', 'danger');
        } finally {
            clearTimeout(timeoutId);
            this.hideLoading('risultato-predizione');
        }
    }

    displayPredictionResult(result) {
        console.log('🎯 Inizio displayPredictionResult con:', result);
        
        const resultDiv = document.getElementById('risultato-predizione');
        console.log('📍 Elemento risultato-predizione:', resultDiv);
        
        if (!resultDiv) {
            console.error('❌ Elemento risultato-predizione non trovato!');
            return;
        }

        // Rimuovi loading overlay
        this.hideLoading('risultato-predizione');
        
        // FORZA la visualizzazione del div
        resultDiv.classList.remove('d-none-custom');
        resultDiv.classList.add('show');
        resultDiv.style.display = 'block !important';
        resultDiv.style.visibility = 'visible';
        
        console.log('✅ Div risultato forzato visibile:', {
            display: resultDiv.style.display,
            visibility: resultDiv.style.visibility,
            classes: resultDiv.className
        });
        
        console.log('🔍 Aggiorno elementi nel risultato...');
        
        try {
            // Aggiorna titolo del match
            const matchTitle = resultDiv.querySelector('#match-title');
            if (matchTitle) {
                matchTitle.textContent = `${result.squadra_casa} vs ${result.squadra_ospite}`;
                console.log('✅ Titolo aggiornato:', matchTitle.textContent);
            } else {
                console.warn('⚠️ Elemento match-title non trovato');
            }

            // Aggiorna predizione
            const predictionBadge = resultDiv.querySelector('#prediction-badge');
            const predictionText = resultDiv.querySelector('#prediction-text');
            if (predictionBadge && predictionText) {
                const predictionLabel = this.getPredictionText(result.predizione);
                predictionText.textContent = predictionLabel;
                predictionBadge.className = `prediction-badge mb-3 ${this.getPredictionClass(result.predizione)}`;
                console.log('✅ Badge predizione aggiornato:', predictionLabel);
            } else {
                console.warn('⚠️ Elementi prediction-badge o prediction-text non trovati', {predictionBadge, predictionText});
            }

            // Aggiorna confidenza
            const confidenceElement = resultDiv.querySelector('#confidence-text');
            const confidenceBar = resultDiv.querySelector('#confidence-bar');
            if (confidenceElement && confidenceBar) {
                const confidencePercentage = Math.round(result.confidenza * 100);
                confidenceElement.textContent = `${confidencePercentage}%`;
                confidenceBar.style.width = `${confidencePercentage}%`;
                confidenceBar.setAttribute('aria-valuenow', confidencePercentage);
                
                // Colore barra basato sulla confidenza
                confidenceBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
                if (confidencePercentage >= 70) {
                    confidenceBar.classList.add('bg-success');
                } else if (confidencePercentage >= 50) {
                    confidenceBar.classList.add('bg-warning');
                } else {
                    confidenceBar.classList.add('bg-danger');
                }
                
                console.log('✅ Confidenza aggiornata:', confidencePercentage + '%');
            } else {
                console.warn('⚠️ Elementi confidence-text o confidence-bar non trovati');
            }

            // Aggiungi badge modalità sistema professionale
            let modalityBadge = resultDiv.querySelector('#modality-badge');
            if (!modalityBadge) {
                modalityBadge = document.createElement('span');
                modalityBadge.id = 'modality-badge';
                modalityBadge.className = 'badge mb-2';
                const matchTitle = resultDiv.querySelector('#match-title');
                if (matchTitle && matchTitle.parentNode) {
                    matchTitle.parentNode.insertBefore(modalityBadge, matchTitle.nextSibling);
                }
            }
            
            // Aggiorna badge basato sulla modalità
            const modalita = result.modalita || 'standard';
            if (modalita === 'professional_deterministic') {
                modalityBadge.textContent = '🔬 Sistema Professionale Deterministico';
                modalityBadge.className = 'badge bg-success mb-2';
            } else if (modalita === 'enhanced') {
                modalityBadge.textContent = '⚡ Sistema Enhanced';
                modalityBadge.className = 'badge bg-info mb-2';
            } else {
                modalityBadge.textContent = '📊 Sistema Standard';
                modalityBadge.className = 'badge bg-secondary mb-2';
            }
            
            // Aggiungi validazione professionale se disponibile
            if (result.validazione) {
                let validationInfo = resultDiv.querySelector('#validation-info');
                if (!validationInfo) {
                    validationInfo = document.createElement('div');
                    validationInfo.id = 'validation-info';
                    validationInfo.className = 'small text-muted mt-2';
                    modalityBadge.parentNode.insertBefore(validationInfo, modalityBadge.nextSibling);
                }
                validationInfo.innerHTML = `
                    <i class="fas fa-check-circle text-success"></i> 
                    Validato: Σ=${result.validazione.somma_probabilita} 
                    ${result.validazione.cache_utilizzata ? '<i class="fas fa-memory text-primary"></i> Cache' : '<i class="fas fa-calculator text-warning"></i> Calcolo'}
                `;
            }
            
            if (result.scraper_integrati) {
                modalityBadge.textContent = '🚀 Enhanced - Scraper Integrati';
                modalityBadge.className = 'badge badge-success mb-2';
                modalityBadge.title = 'Predizione con dati live: quote, infortuni, meteo, sentiment';
            } else {
                modalityBadge.textContent = '📊 Standard - Solo ML';
                modalityBadge.className = 'badge badge-secondary mb-2';
                modalityBadge.title = 'Predizione basata solo su modelli Machine Learning e dati storici';
            }

            // Aggiorna probabilità
            if (result.probabilita) {
                console.log('📊 Aggiorno probabilità:', result.probabilita);
                
                const probHome = resultDiv.querySelector('#prob-casa');
                const probDraw = resultDiv.querySelector('#prob-pareggio');
                const probAway = resultDiv.querySelector('#prob-trasferta');
                
                if (probHome && probDraw && probAway) {
                    probHome.textContent = Math.round(result.probabilita.H * 100) + '%';
                    probDraw.textContent = Math.round(result.probabilita.D * 100) + '%';
                    probAway.textContent = Math.round(result.probabilita.A * 100) + '%';
                    console.log('✅ Probabilità aggiornate');
                } else {
                    console.warn('⚠️ Alcuni elementi probabilità non trovati:', {probHome, probDraw, probAway});
                }
            }

            // Aggiorna raccomandazione
            const recommendationText = resultDiv.querySelector('#recommendation-text');
            if (recommendationText) {
                const recommendation = this.getRecommendationText(result.predizione, result.confidenza);
                recommendationText.textContent = recommendation;
                console.log('✅ Raccomandazione aggiornata:', recommendation);
            }

            // Aggiorna grafico probabilità se disponibile
            if (result.probabilita) {
                this.updateProbabilityChart(result.probabilita);
                console.log('📊 Grafico probabilità aggiornato');
            }
            
            console.log('🎉 displayPredictionResult completato con successo!');
            
        } catch (error) {
            console.error('❌ Errore in displayPredictionResult:', error);
        }
    }

    formatPrediction(predizione) {
        const predictions = {
            'H': 'Vittoria Casa',
            'D': 'Pareggio',
            'A': 'Vittoria Ospite'
        };
        return predictions[predizione] || predizione;
    }

    getPredictionClass(predizione) {
        const classes = {
            'H': 'text-success',
            'D': 'text-warning',
            'A': 'text-info'
        };
        return classes[predizione] || '';
    }

    getPredictionText(predizione) {
        const predictions = {
            'H': 'Vittoria Casa',
            'D': 'Pareggio',
            'A': 'Vittoria Ospite'
        };
        return predictions[predizione] || predizione;
    }

    getRecommendationText(prediction, confidence) {
        const confidencePercentage = Math.round(confidence * 100);
        const predictionText = this.getPredictionText(prediction);
        
        if (confidencePercentage >= 70) {
            return `Consiglio forte: ${predictionText} (${confidencePercentage}% di confidenza)`;
        } else if (confidencePercentage >= 50) {
            return `Consiglio moderato: ${predictionText} (${confidencePercentage}% di confidenza)`;
        } else {
            return `Risultato incerto, evitare scommesse (${confidencePercentage}% di confidenza)`;
        }
    }

    updateConfidenceMeter(confidenza) {
        const progressBar = document.querySelector('#confidence-bar');
        const confidenceText = document.getElementById('confidence-text');
        
        const percentage = Math.round(confidenza * 100);
        
        setTimeout(() => {
            progressBar.style.width = `${percentage}%`;
            progressBar.textContent = `${percentage}%`;
            confidenceText.textContent = `${percentage}%`;
            
            // Update color based on confidence
            progressBar.className = 'progress-bar ' + this.getConfidenceClass(confidenza);
        }, 10); // Ridotto da 100ms a 10ms
    }

    getConfidenceClass(confidenza) {
        if (confidenza >= 0.7) return 'bg-success';
        if (confidenza >= 0.5) return 'bg-warning';
        return 'bg-danger';
    }

    updateRecommendation(confidenza) {
        const recommendationDiv = document.getElementById('recommendation');
        let classe, testo;

        if (confidenza >= 0.7) {
            classe = 'alta';
            testo = 'Predizione ad alta confidenza - Raccomandata';
        } else if (confidenza >= 0.5) {
            classe = 'media';
            testo = 'Predizione a media confidenza - Valutare attentamente';
        } else {
            classe = 'bassa';
            testo = 'Predizione a bassa confidenza - Non raccomandata';
        }

        recommendationDiv.className = `recommendation ${classe}`;
        recommendationDiv.innerHTML = `<i class="fas fa-lightbulb"></i> ${testo}`;
    }

    updateProbabilityChart(probabilita) {
        // Update detail cards (con controlli di sicurezza)
        const probCasa = document.getElementById('prob-casa');
        const probPareggio = document.getElementById('prob-pareggio');
        const probTrasferta = document.getElementById('prob-trasferta');
        
        if (probCasa) probCasa.textContent = `${Math.round(probabilita.H * 100)}%`;
        if (probPareggio) probPareggio.textContent = `${Math.round(probabilita.D * 100)}%`;
        if (probTrasferta) probTrasferta.textContent = `${Math.round(probabilita.A * 100)}%`;

        // Create/update chart
        const ctx = document.getElementById('probability-chart');
        if (!ctx) {
            console.warn('⚠️ Elemento probability-chart non trovato, salto aggiornamento grafico');
            return;
        }
        
        // Distruggi grafico esistente in modo sicuro
        if (this.charts.probability) {
            this.charts.probability.destroy();
            this.charts.probability = null;
        }
        
        // Verifica che la canvas non abbia già un grafico associato
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        this.charts.probability = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Vittoria Casa', 'Pareggio', 'Vittoria Ospite'],
                datasets: [{
                    data: [
                        Math.round(probabilita.H * 100),
                        Math.round(probabilita.D * 100),
                        Math.round(probabilita.A * 100)
                    ],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#17a2b8'
                    ],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
    }

    async getFormaSquadra() {
        const squadra = document.getElementById('squadra-forma').value;
        
        if (!squadra) {
            this.showAlert('Seleziona una squadra', 'warning');
            return;
        }

        this.showLoading('btn-analizza-forma');
        const btnElement = document.getElementById('btn-analizza-forma');
        if (btnElement) {
            btnElement.disabled = true;
            btnElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Caricamento...';
        }

        try {
            const response = await fetch(`/api/forma/${squadra}`);
            
            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    this.displayFormaResults(data);
                } else {
                    console.error('❌ Risposta non JSON per forma squadra:', contentType);
                    this.showAlert('Errore: risposta non valida dal server', 'danger');
                }
            } else {
                console.error('❌ Errore HTTP forma squadra:', response.status);
                this.showAlert('Errore nel caricamento forma', 'danger');
            }
        } catch (error) {
            console.error('Errore:', error);
            this.showAlert('Errore di connessione', 'danger');
        } finally {
            this.hideLoading('btn-analizza-forma');
            const btnElement = document.getElementById('btn-analizza-forma');
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.innerHTML = '<i class="fas fa-analytics me-2"></i>Analizza';
            }
        }
    }

    displayFormaResults(data) {
        const resultsDiv = document.getElementById('risultati-forma');
        
        // Update team name
        const titleElement = document.getElementById('forma-squadra-title');
        if (titleElement) {
            titleElement.innerHTML = `<i class="fas fa-shield-alt me-2"></i>${data.squadra}`;
        }

        // Update stats con gli ID corretti dal template
        const formaPartite = document.getElementById('forma-partite');
        const formaVittorie = document.getElementById('forma-vittorie');
        const formaPareggi = document.getElementById('forma-pareggi');
        const formaSconfitte = document.getElementById('forma-sconfitte');
        const formaGolFatti = document.getElementById('forma-gol-fatti');
        const formaGolSubiti = document.getElementById('forma-gol-subiti');
        const formaMediaFatti = document.getElementById('forma-media-fatti');
        const formaMediaSubiti = document.getElementById('forma-media-subiti');
        
        if (formaPartite) formaPartite.textContent = data.partite_analizzate || data.partite?.length || 0;
        if (formaVittorie) formaVittorie.textContent = data.vittorie || data.statistiche?.vittorie || 0;
        if (formaPareggi) formaPareggi.textContent = data.pareggi || data.statistiche?.pareggi || 0;
        if (formaSconfitte) formaSconfitte.textContent = data.sconfitte || data.statistiche?.sconfitte || 0;
        if (formaGolFatti) formaGolFatti.textContent = data.gol_fatti || data.statistiche?.gol_fatti || 0;
        if (formaGolSubiti) formaGolSubiti.textContent = data.gol_subiti || data.statistiche?.gol_subiti || 0;
        if (formaMediaFatti) formaMediaFatti.textContent = data.media_gol_fatti || 0;
        if (formaMediaSubiti) formaMediaSubiti.textContent = data.media_gol_subiti || 0;

        // Update form visualization - converti stringa in array se necessario
        const formaString = data.forma || data.statistiche?.forma || '';
        this.updateFormaVisualization(formaString);

        // Popola la tabella dei risultati
        this.populateResultsTable(data.partite || []);

        // Show results
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    populateResultsTable(partite) {
        const tbody = document.getElementById('forma-risultati-body');
        
        if (!tbody) {
            console.warn('Tabella risultati non trovata');
            return;
        }

        tbody.innerHTML = '';

        if (!partite || partite.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nessun risultato disponibile</td></tr>';
            return;
        }

        partite.forEach(partita => {
            const row = document.createElement('tr');
            
            // Badge per l'esito
            const esitoClass = partita.esito === 'V' ? 'success' : (partita.esito === 'P' ? 'warning' : 'danger');
            const esitoText = partita.esito === 'V' ? 'Vittoria' : (partita.esito === 'P' ? 'Pareggio' : 'Sconfitta');
            
            row.innerHTML = `
                <td>${partita.data || 'N/A'}</td>
                <td><strong>${partita.avversario || 'N/A'}</strong></td>
                <td>
                    <span class="badge bg-${partita.casa ? 'primary' : 'secondary'}">
                        ${partita.casa ? 'Casa' : 'Trasferta'}
                    </span>
                </td>
                <td>
                    <span class="badge bg-${esitoClass}">
                        ${partita.risultato || 'N/A'}
                    </span>
                </td>
                <td>
                    <span class="badge bg-${esitoClass}" title="${esitoText}">
                        ${partita.esito || 'N/A'}
                    </span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    updateFormaVisualization(formaRecente) {
        const formaContainer = document.getElementById('forma-visual');
        formaContainer.innerHTML = '';

        if (formaRecente && formaRecente.length > 0) {
            // Se è una stringa, convertila in array
            const risultati = Array.isArray(formaRecente) ? formaRecente : formaRecente.split('');
            
            risultati.forEach(risultato => {
                if (risultato && (risultato === 'V' || risultato === 'P' || risultato === 'S')) {
                    const badge = document.createElement('div');
                    badge.className = `forma-badge ${risultato}`;
                    badge.textContent = risultato;
                    badge.title = this.getResultTitle(risultato);
                    formaContainer.appendChild(badge);
                }
            });
        } else {
            formaContainer.innerHTML = '<p class="text-muted">Nessun dato disponibile</p>';
        }
    }

    getResultTitle(risultato) {
        const titles = {
            'V': 'Vittoria',
            'P': 'Pareggio',
            'S': 'Sconfitta'
        };
        return titles[risultato] || risultato;
    }

    async loadStatistiche() {
        console.log('📊 Caricamento statistiche ottimizzato...');
        
        // Cache check potenziato
        if (this.statistiche && Date.now() - this.lastStatsLoad < 60000) {
            console.log('📊 Uso cache statistiche (valida)');
            // Aggiornamento asincrono ottimizzato
            setTimeout(() => this.updateStatistiche(this.statistiche), 0);
            return;
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000); // Timeout ragionevole per API
            
            const response = await fetch('/api/statistiche', {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`Expected JSON response, got: ${contentType}`);
            }
            
            const data = await response.json();
            console.log('📊 Dati statistiche ricevuti');
            
            this.statistiche = data;
            this.lastStatsLoad = Date.now();
            
            // Aggiornamento asincrono ottimizzato
            setTimeout(() => this.updateStatistiche(data), 0);
            
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('⚠️ Timeout statistiche');
                this.showAlert('Caricamento statistiche lento, riprova più tardi', 'warning');
            } else {
                console.error('❌ Errore:', error);
                this.showAlert('Errore di connessione alle statistiche', 'danger');
            }
        }
    }

    updateStatistiche(data) {
        // Ottimizzazione: aggiorna solo elementi visibili
        const updates = [];
        
        if (data.stats_generali) {
            const elements = {
                'stat-partite': data.stats_generali.totale_partite || 0,
                'stat-squadre': data.stats_generali.squadre_totali || 0,
                'stat-gol': data.stats_generali.media_gol_partita || 0,
                'stat-periodo': data.stats_generali.periodo || 'Serie A 2025-26'
            };
            
            // Batch DOM updates ottimizzato con setTimeout
            setTimeout(() => {
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element && element.textContent !== String(value)) {
                        element.textContent = value;
                    }
                });
                console.log('✅ Statistiche aggiornate in batch');
            }, 0);
        }
        
        // Aggiorna grafici con dati disponibili
        if (data.distribuzione_risultati) {
            // Converti formato API per compatibilità grafico
            const distribuzioneFormatted = {
                H: data.distribuzione_risultati.vittorie_casa || 0,
                D: data.distribuzione_risultati.pareggi || 0,
                A: data.distribuzione_risultati.vittorie_trasferta || 0
            };
            this.updateResultsChart(distribuzioneFormatted);
        }
        
        // Se disponibili, carica dati di accuratezza per grafici aggiuntivi
        if (!data.accuracy_by_market) {
            this.loadAccuracyData();
        } else {
            this.updateAccuracyChart(data.accuracy_by_market);
        }
        
        
        
        console.log('✅ Statistiche aggiornate');
    }

    async loadAccuracyData() {
        try {
            const response = await fetch('/api/accuracy_report');
            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.accuracy_by_market) {
                        this.updateAccuracyChart(data.accuracy_by_market);
                    }
                } else {
                    console.warn('⚠️ Risposta non JSON per accuracy report:', contentType);
                }
            }
        } catch (error) {
            console.warn('⚠️ Errore caricamento dati accuratezza:', error);
        }
    }

    updateAccuracyChart(accuratezzaModelli) {
        if (!accuratezzaModelli) return;

        const ctx = document.getElementById('accuracy-chart');
        if (!ctx) {
            console.warn('⚠️ Elemento accuracy-chart non trovato');
            return;
        }
        
        // Distruggi grafico esistente in modo sicuro
        if (this.charts.accuracy) {
            this.charts.accuracy.destroy();
            this.charts.accuracy = null;
        }
        
        // Verifica che la canvas non abbia già un grafico associato
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        this.charts.accuracy = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(accuratezzaModelli),
                datasets: [{
                    label: 'Accuratezza (%)',
                    data: Object.values(accuratezzaModelli),
                    backgroundColor: [
                        'rgba(0, 102, 204, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)'
                    ],
                    borderColor: [
                        'rgba(0, 102, 204, 1)',
                        'rgba(40, 167, 69, 1)',
                        'rgba(255, 193, 7, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    updateResultsChart(distribuzioneRisultati) {
        if (!distribuzioneRisultati) return;

        const ctx = document.getElementById('results-chart');
        if (!ctx) {
            console.warn('⚠️ Elemento results-chart non trovato');
            return;
        }
        
        // Distruggi grafico esistente in modo sicuro
        if (this.charts.results) {
            this.charts.results.destroy();
            this.charts.results = null;
        }
        
        // Verifica che la canvas non abbia già un grafico associato
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        this.charts.results = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Vittorie Casa', 'Pareggi', 'Vittorie Ospite'],
                datasets: [{
                    data: [
                        distribuzioneRisultati.H || 0,
                        distribuzioneRisultati.D || 0,
                        distribuzioneRisultati.A || 0
                    ],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#17a2b8'
                    ],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initCharts() {
        // Initialize empty charts
        Chart.defaults.font.family = 'Inter';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#666';
    }

    loadSystemInfo() {
        // System information is static for now
        console.log('Loading system info...');
    }

    updateConnectionStatus(connected = true) {
        console.log('🔄 Aggiornamento connection status:', connected);
        
        const statusElement = document.getElementById('status-text');
        if (!statusElement) {
            console.warn('⚠️ Elemento status-text non trovato');
            return;
        }
        
        // Sistema HTTP sempre connesso
        statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Sistema Professionale Operativo';
        statusElement.className = 'text-success';
        
        console.log('✅ Status: Sistema operativo');
    }

    showLoading(elementId) {
        console.log('🔄 Mostra loading per:', elementId);
        const element = document.getElementById(elementId);
        if (element) {
            // Invece di sostituire tutto, mostra solo il div e aggiungi una classe loading
            element.style.display = 'block';
            element.classList.add('loading');
            
            // Aggiungi overlay loading invece di sostituire contenuto
            let loadingOverlay = element.querySelector('.loading-overlay');
            if (!loadingOverlay) {
                loadingOverlay = document.createElement('div');
                loadingOverlay.className = 'loading-overlay';
                loadingOverlay.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(255,255,255,0.9);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                `;
                element.style.position = 'relative';
                element.appendChild(loadingOverlay);
            }
            
            loadingOverlay.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Caricamento...</span>
                    </div>
                    <p class="mt-3">Caricamento in corso...</p>
                </div>
            `;
            console.log('✅ Loading overlay aggiunto');
        } else {
            console.warn('⚠️ Elemento non trovato:', elementId);
        }
    }

    hideLoading(elementId) {
        console.log('✅ Nascondi loading per:', elementId);
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('loading');
            const loadingOverlay = element.querySelector('.loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.remove();
            }
            
            // Assicurati che l'elemento sia visibile dopo aver rimosso il loading
            element.style.display = 'block';
            element.classList.remove('d-none', 'd-none-custom');
            
            console.log('🔍 Elemento ora visibile:', elementId);
        }
    }

    showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)}"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Find a container for alerts or create one
        let alertContainer = document.getElementById('alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alert-container';
            alertContainer.className = 'position-fixed top-0 end-0 p-3';
            alertContainer.style.zIndex = '1050';
            document.body.appendChild(alertContainer);
        }
        
        const alertElement = document.createElement('div');
        alertElement.innerHTML = alertHtml;
        alertContainer.appendChild(alertElement.firstElementChild);
        
        // Auto-remove after 3 seconds (ridotto per performance)
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 3000); // Ridotto da 5000ms a 3000ms
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Mercati Multipli Methods
    async makeMercatiPrediction() {
        console.log('🎲 Inizio analisi mercati multipli...');
        
        const squadraCasa = document.getElementById('mercati-squadra-casa').value;
        const squadraTrasferta = document.getElementById('mercati-squadra-trasferta').value;

        console.log('🏟️ Squadre per mercati:', squadraCasa, 'vs', squadraTrasferta);

        if (!squadraCasa || !squadraTrasferta) {
            console.warn('⚠️ Squadre mancanti per mercati');
            this.showAlert('Seleziona entrambe le squadre per l\'analisi mercati', 'warning');
            return;
        }

        if (squadraCasa === squadraTrasferta) {
            console.warn('⚠️ Squadre identiche per mercati');
            this.showAlert('Seleziona squadre diverse per l\'analisi mercati', 'warning');
            return;
        }

        console.log('📡 Invio richiesta API mercati...');
        this.showLoading('risultati-mercati');

        try {
            const response = await fetch('/api/mercati', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    squadra_casa: squadraCasa,
                    squadra_ospite: squadraTrasferta
                })
            });

            console.log('📊 Risposta API mercati ricevuta:', response.status);

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}`;
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.error || errorMessage;
                    } catch (e) {
                        console.warn('⚠️ Errore parsing JSON di errore:', e);
                    }
                }
                throw new Error(errorMessage);
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`Expected JSON response, got: ${contentType}`);
            }

            const data = await response.json();
            console.log('✅ Dati mercati OK, chiamata displayMercatiResults...');
            this.displayMercatiResults(data);

        } catch (error) {
            console.error('❌ Errore richiesta mercati:', error);
            this.hideLoading('risultati-mercati');
            this.showAlert(`Errore nell'analisi mercati: ${error.message}`, 'danger');
        }
    }

    displayMercatiResults(data) {
        console.log('🎯 Inizio displayMercatiResults PROFESSIONALE con:', data);
        
        const risultatiDiv = document.getElementById('risultati-mercati');
        if (!risultatiDiv) {
            console.error('❌ Elemento risultati-mercati non trovato');
            return;
        }

        // SISTEMA DETERMINISTICO - Visualizzazione garantita
        this.hideLoading('risultati-mercati');
        
        // FORZA visualizzazione - Sistema sicuro e garantito
        risultatiDiv.classList.remove('d-none-custom');
        risultatiDiv.classList.add('show');
        risultatiDiv.style.display = 'block';
        risultatiDiv.style.visibility = 'visible';
        
        console.log('✅ Sistema PROFESSIONALE - Visualizzazione garantita');

        // SISTEMA DETERMINISTICO - Genera HTML completo e garantito
        const htmlContent = this.generaHTMLMercatiDeterministico(data);
        risultatiDiv.innerHTML = htmlContent;
        
        console.log('🎉 Sistema mercati PROFESSIONALE completato al 100%');
    }

    generaHTMLMercatiDeterministico(data) {
        console.log('🔧 Generazione HTML deterministica per mercati:', data);
        
        const partitaTitle = `${data.squadra_casa} vs ${data.squadra_ospite}`;
        const mercati = data.mercati || {};
        const timestamp = new Date(data.timestamp).toLocaleTimeString('it-IT');
        const confidenceGenerale = data.predizione_principale?.confidenza || 0;
        
        let html = `
        <div class="card shadow-lg border-0">
            <div class="card-header bg-gradient text-white" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h5 class="mb-0">
                    <i class="fas fa-chart-line me-2"></i>
                    Analisi Mercati Multipli - ${partitaTitle}
                </h5>
                <small class="opacity-75">Aggiornato: ${timestamp} | Modalità: ${data.modalita || 'Professional'}</small>
            </div>
            <div class="card-body">
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="text-center">
                            <h6 class="text-muted">Confidenza Generale</h6>
                            <span class="h4 text-primary">${(confidenceGenerale * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h6 class="text-muted">Mercati Analizzati</h6>
                            <span class="h4 text-success">${Object.keys(mercati).length}</span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h6 class="text-muted">Sistema</h6>
                            <span class="h6 text-info">Deterministico</span>
                        </div>
                    </div>
                </div>
        `;
        
        // Genera sezioni per ogni mercato in modo deterministico
        Object.entries(mercati).forEach(([key, mercato]) => {
            if (mercato && typeof mercato === 'object') {
                html += this.generaSezioneMarketoDeterministico(key, mercato);
            }
        });
        
        html += `
            </div>
        </div>
        `;
        
        return html;
    }

    generaSezioneMarketoDeterministico(chiave, mercato) {
        const nome = mercato.nome || chiave;
        const confidenza = mercato.confidenza || 0;
        const consiglio = mercato.consiglio || 'N/A';
        const probabilita = mercato.probabilita || {};
        
        let sezioneHTML = `
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-light">
                    <div class="card-header bg-light">
                        <h6 class="mb-0">
                            <i class="fas fa-dice me-2"></i>
                            ${nome}
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <strong>Consiglio:</strong><br>
                                <span class="badge bg-primary fs-6">${consiglio}</span>
                            </div>
                            <div class="col-md-3">
                                <strong>Confidenza:</strong><br>
                                <span class="text-success fw-bold">${(confidenza * 100).toFixed(1)}%</span>
                            </div>
                            <div class="col-md-6">
                                <strong>Probabilità:</strong><br>
                                ${this.generaProbabilitaBars(probabilita)}
                            </div>
                        </div>
        `;
        
        // Aggiungi informazioni extra se disponibili
        if (mercato.gol_previsti) {
            sezioneHTML += `
                        <div class="row mt-2">
                            <div class="col-12">
                                <small class="text-muted">
                                    <i class="fas fa-futbol me-1"></i>
                                    Goal previsti: <strong>${mercato.gol_previsti}</strong>
                                </small>
                            </div>
                        </div>
            `;
        }
        
        sezioneHTML += `
                    </div>
                </div>
            </div>
        </div>
        `;
        
        return sezioneHTML;
    }

    generaProbabilitaBars(probabilita) {
        let barsHTML = '';
        Object.entries(probabilita).forEach(([key, value]) => {
            const percentage = (value * 100).toFixed(1);
            const label = this.formatLabel(key);
            
            barsHTML += `
                <div class="mb-1">
                    <small class="d-flex justify-content-between">
                        <span>${label}</span>
                        <span><strong>${percentage}%</strong></span>
                    </small>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar ${this.getColorClass(value)}" 
                             style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        });
        return barsHTML;
    }

    formatLabel(key) {
        const labels = {
            'H': 'Casa',
            'D': 'Pareggio', 
            'A': 'Trasferta',
            'over': 'Over',
            'under': 'Under',
            'goal': 'Goal',
            'nogoal': 'No Goal'
        };
        return labels[key] || key;
    }

    getColorClass(value) {
        if (value >= 0.6) return 'bg-success';
        if (value >= 0.4) return 'bg-warning';
        return 'bg-danger';
    }

    // Metodo per pulire tutti i grafici Chart.js
    destroyAllCharts() {
        console.log('🧹 Pulizia completa di tutti i grafici Chart.js...');
        
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                try {
                    this.charts[chartKey].destroy();
                    this.charts[chartKey] = null;
                    console.log(`✅ Grafico ${chartKey} distrutto`);
                } catch (error) {
                    console.warn(`⚠️ Errore distruzione grafico ${chartKey}:`, error);
                }
            }
        });
        
        // Pulisci anche eventuali grafici registrati globalmente
        Chart.helpers.each(Chart.instances, function(instance) {
            try {
                instance.destroy();
                console.log('✅ Istanza Chart.js globale distrutta');
            } catch (error) {
                console.warn('⚠️ Errore distruzione istanza globale:', error);
            }
        });
        
        this.charts = {};
        console.log('✅ Pulizia grafici completata');
    }
}

// Global error handlers to prevent extension interference
window.addEventListener('error', function(event) {
    // Filter out extension-related errors
    const message = event.message || '';
    if (message.includes('runtime.lastError') || 
        message.includes('message channel closed') ||
        message.includes('Extension context invalidated')) {
        event.preventDefault();
        return false;
    }
}, true);

window.addEventListener('unhandledrejection', function(event) {
    // Filter out extension-related promise rejections
    const reason = event.reason || '';
    const reasonStr = reason.toString ? reason.toString() : String(reason);
    if (reasonStr.includes('runtime.lastError') || 
        reasonStr.includes('message channel closed') ||
        reasonStr.includes('Extension context invalidated')) {
        event.preventDefault();
        return false;
    }
});

// Inizializzazione app quando DOM è caricato - Sistema Deterministico
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 DOM caricato, inizializzazione ultra-rapida...');
    
    // Verifica che non ci sia già un'istanza
    if (window.pronosticiApp) {
        console.log('⚠️ App già inizializzata, skip duplicazione');
        return;
    }
    
    // Cleanup eventuali listener rimasti
    try {
        // Rimuovi eventuali chart instance globali
        if (typeof Chart !== 'undefined') {
            Chart.helpers.each(Chart.instances, function(instance) {
                if (instance) {
                    instance.destroy();
                }
            });
        }
        
        // Suppress chrome extension runtime errors
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.lastError) {
            // Ignore lastError to prevent console spam
            chrome.runtime.lastError = null;
        }
    } catch (error) {
        // Silently ignore extension-related cleanup errors
        if (!error.message || (!error.message.includes('runtime.lastError') && 
            !error.message.includes('Extension context invalidated'))) {
            console.warn('⚠️ Cleanup chart instances:', error);
        }
    }
    
    // Inizializzazione immediata leggera senza requestAnimationFrame
    window.pronosticiApp = new PronosticiApp();
    console.log('✅ App inizializzata istantaneamente!');
}, { once: true }); // Usa once per evitare listener multipli

// Cleanup quando la pagina viene scaricata
window.addEventListener('beforeunload', function() {
    if (window.pronosticiApp && typeof window.pronosticiApp.destroyAllCharts === 'function') {
        window.pronosticiApp.destroyAllCharts();
    }
}, { once: true });

// Funzione globale per test debug
window.testSezioni = function() {
    console.log('🧪 Test debug sezioni avviato');
    
    // Test immediato caricamento statistiche con timeout
    const controller1 = new AbortController();
    const timeoutId1 = setTimeout(() => controller1.abort(), 5000);
    
    fetch('/api/statistiche', { signal: controller1.signal })
        .then(response => {
            clearTimeout(timeoutId1);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`Expected JSON response, got: ${contentType}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Test statistiche:', data);
        })
        .catch(error => {
            clearTimeout(timeoutId1);
            if (error.name !== 'AbortError') {
                console.error('❌ Errore test statistiche:', error);
            }
        });

    // Test forma squadra con timeout
    const controller2 = new AbortController();
    const timeoutId2 = setTimeout(() => controller2.abort(), 5000);
    
    fetch('/api/forma/Pisa', { signal: controller2.signal })
        .then(response => {
            clearTimeout(timeoutId2);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error(`Expected JSON response, got: ${contentType}`);
            }
            return response.json();
        })  
        .then(data => {
            console.log('📈 Test forma squadra:', data);
        })
        .catch(error => {
            clearTimeout(timeoutId2);
            if (error.name !== 'AbortError') {
                console.error('❌ Errore test forma:', error);
            }
        });
    
    console.log('✅ Test debug completato');
};

// Utility Functions
function formatNumber(num) {
    return new Intl.NumberFormat('it-IT').format(num);
}

function formatPercentage(num) {
    return `${Math.round(num * 100)}%`;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('it-IT');
}

// Funzione globale per test debug
window.testSezioni = function() {
    console.log('🧪 Test debug sezioni avviato');
    
    // Test immediato caricamento statistiche
    fetch('/api/statistiche')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Statistiche API:', data);
            alert('Statistiche: ' + JSON.stringify(data.stats_generali, null, 2));
        })
        .catch(error => {
            console.error('❌ Errore statistiche:', error);
            alert('Errore statistiche: ' + error.message);
        });
    
    // Test forma Pisa
    fetch('/api/forma/Pisa')
        .then(response => response.json())
        .then(data => {
            console.log('🏴‍☠️ Forma Pisa:', data);
            alert('Forma Pisa: ' + data.forma + ' (' + data.partite_analizzate + ' partite)');
        })
        .catch(error => {
            console.error('❌ Errore forma:', error);
            alert('Errore forma: ' + error.message);
        });
};

// Export for global access
window.PronosticiApp = PronosticiApp;

// Funzione di test globale
window.testPredizione = function() {
    console.log('🧪 Test predizione manuale...');
    
    // Trova i dropdown
    const casaSelect = document.getElementById('squadra-casa');
    const ospiteSelect = document.getElementById('squadra-trasferta');
    
    if (!casaSelect || !ospiteSelect) {
        console.error('❌ Dropdown non trovati');
        console.log('Casa:', casaSelect);
        console.log('Ospite:', ospiteSelect);
        return;
    }
    
    // Mostra le opzioni disponibili
    console.log('📋 Opzioni casa:', casaSelect.options.length);
    console.log('📋 Opzioni ospite:', ospiteSelect.options.length);
    
    // Imposta valori
    casaSelect.value = 'Inter';
    ospiteSelect.value = 'Juventus';
    
    console.log('✅ Valori impostati:', casaSelect.value, 'vs', ospiteSelect.value);
    
    // Verifica che i valori siano stati impostati
    if (!casaSelect.value || !ospiteSelect.value) {
        console.error('❌ Valori non impostati correttamente');
        console.log('⚠️ Probabilmente le squadre non sono nella lista');
        console.log('Prime 5 opzioni casa:');
        for (let i = 1; i < Math.min(6, casaSelect.options.length); i++) {
            console.log(`  ${i}: ${casaSelect.options[i].value}`);
        }
        
        // Prova con le prime squadre disponibili
        if (casaSelect.options.length > 2 && ospiteSelect.options.length > 3) {
            casaSelect.value = casaSelect.options[1].value;
            ospiteSelect.value = ospiteSelect.options[2].value;
            console.log('🔄 Retry con:', casaSelect.value, 'vs', ospiteSelect.value);
        } else {
            return;
        }
    }
    
    // Simula predizione
    if (window.pronosticiApp) {
        console.log('🔮 Chiamata makePrediction...');
        window.pronosticiApp.makePrediction();
    } else {
        console.error('❌ App non disponibile');
    }
};

// Funzione di test per la navigazione
window.testNavigazione = function() {
    console.log('🧪 Test navigazione avviato...');
    
    const sezioni = ['predizioni', 'mercati', 'statistiche', 'forma', 'info'];
    let indice = 0;
    
    function testSezione() {
        if (indice < sezioni.length) {
            const sezione = sezioni[indice];
            console.log(`🔄 Test sezione: ${sezione}`);
            
            if (window.pronosticiApp) {
                window.pronosticiApp.switchSection(sezione);
                
                // Verifica che la sezione sia visibile
                setTimeout(() => {
                    const elemento = document.getElementById(sezione);
                    const link = document.querySelector(`[data-section="${sezione}"]`);
                    
                    if (elemento && elemento.classList.contains('active')) {
                        console.log(`✅ Sezione ${sezione}: OK`);
                    } else {
                        console.error(`❌ Sezione ${sezione}: ERRORE`);
                    }
                    
                    if (link && link.classList.contains('active')) {
                        console.log(`✅ Link ${sezione}: OK`);
                    } else {
                        console.error(`❌ Link ${sezione}: ERRORE`);
                    }
                    
                    indice++;
                    // Usa setTimeout per test non bloccanti
                    setTimeout(() => testSezione(), 0);
                }, 500);
            }
        } else {
            console.log('🎉 Test navigazione completato!');
            // Torna alla sezione predizioni
            if (window.pronosticiApp) {
                window.pronosticiApp.switchSection('predizioni');
            }
        }
    }
    
    testSezione();
};

console.log('🧪 Funzioni di test disponibili: window.testPredizione(), window.testNavigazione()');