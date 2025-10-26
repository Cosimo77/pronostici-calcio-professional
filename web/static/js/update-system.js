// ==================== SISTEMA AGGIORNAMENTO DATI ====================

// Sistema Aggiornamento Dati
window.aggiornaSystema = async function() {
    console.log('🔄 Richiesta aggiornamento sistema...');
    
    const btnAggiorna = document.getElementById('btn-aggiorna-sistema');
    if (!btnAggiorna) {
        console.error('❌ Pulsante aggiornamento non trovato');
        return;
    }
    
    // Controlla se già in corso
    if (btnAggiorna.disabled) {
        console.log('⚠️ Aggiornamento già in corso');
        return;
    }
    
    // Conferma dall'utente
    const conferma = confirm(
        '🔄 Aggiornare il sistema con i dati più recenti?\n\n' +
        '• Scaricherà nuove partite Serie A\n' +
        '• Riaddestrerà i modelli ML\n' +
        '• Tempo stimato: 3-5 minuti\n\n' +
        'Procedere?'
    );
    
    if (!conferma) {
        console.log('❌ Aggiornamento annullato dall\'utente');
        return;
    }
    
    try {
        // Disabilita il pulsante e mostra stato
        btnAggiorna.disabled = true;
        btnAggiorna.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Aggiornamento...';
        btnAggiorna.className = 'btn btn-secondary btn-sm ms-2';
        
        // Mostra notifica di avvio
        showStatusMessage('🚀 Aggiornamento sistema avviato...', 'info');
        
        // Richiesta API
        const response = await fetch('/api/aggiorna-sistema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                console.log('✅ Aggiornamento avviato:', data);
                showStatusMessage(
                    `🔄 ${data.message} (${data.estimated_time})`,
                    'warning'
                );
                
                // Avvia il polling dello status
                pollUpdateStatus();
            } else {
                console.error('❌ Risposta non JSON per update:', contentType);
                showStatusMessage('Errore: risposta non valida dal server', 'danger');
            }
        } else {
            console.error('❌ Errore HTTP update:', response.status);
            showStatusMessage('Errore del server', 'danger');
        }
        
    } catch (error) {
        console.error('💥 Errore richiesta aggiornamento:', error);
        resetUpdateButton();
        showStatusMessage('💥 Errore di connessione', 'danger');
    }
};

// Reset pulsante aggiornamento
function resetUpdateButton() {
    const btnAggiorna = document.getElementById('btn-aggiorna-sistema');
    if (btnAggiorna) {
        btnAggiorna.disabled = false;
        btnAggiorna.innerHTML = '<i class="fas fa-sync-alt me-1"></i>Aggiorna Dati';
        btnAggiorna.className = 'btn btn-warning btn-sm ms-2';
    }
}

// Mostra messaggio di status
function showStatusMessage(message, type = 'info') {
    const statusBar = document.getElementById('status-bar');
    const statusText = document.getElementById('status-text');
    
    if (statusBar && statusText) {
        statusText.textContent = message;
        statusBar.className = `alert alert-${type} alert-dismissible fade show mb-0`;
        statusBar.style.display = 'block';
        
        // Auto-hide per messaggi non critici
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                statusBar.style.display = 'none';
            }, 5000);
        }
    }
}

// Polling status aggiornamento
function pollUpdateStatus() {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status-aggiornamento');
            
            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    console.log('📊 Status aggiornamento:', data);
                    
                    if (data.status === 'idle') {
                        clearInterval(pollInterval);
                        resetUpdateButton();
                        console.log('✅ Aggiornamento completato (idle)');
                        
                    } else if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        resetUpdateButton();
                showStatusMessage('🎉 Sistema aggiornato con successo!', 'success');
                console.log('✅ Aggiornamento completato con successo');
                
                // Opzionalmente ricarica componenti
                setTimeout(() => {
                    if (confirm('🔄 Vuoi ricaricare la pagina per applicare gli aggiornamenti?')) {
                        window.location.reload();
                    }
                }, 2000);
                
            } else if (data.status === 'error') {
                clearInterval(pollInterval);
                resetUpdateButton();
                showStatusMessage(`❌ Errore: ${data.error || 'Errore sconosciuto'}`, 'danger');
                console.error('❌ Aggiornamento fallito:', data.error);
                
                    } else if (data.status === 'running') {
                        // Aggiornamento in corso, continua polling
                        showStatusMessage('🔄 Aggiornamento in corso...', 'info');
                    }
                } else {
                    console.warn('⚠️ Risposta non JSON per status:', response.headers.get('content-type'));
                }
            } else {
                console.error('❌ Errore HTTP status:', response.status);
            }
            
        } catch (error) {
            console.error('⚠️ Errore polling status:', error);
            clearInterval(pollInterval);
            resetUpdateButton();
            showStatusMessage('⚠️ Errore controllo stato', 'warning');
        }
    }, 3000); // Controlla ogni 3 secondi
    
    // Timeout sicurezza: ferma polling dopo 15 minuti
    setTimeout(() => {
        clearInterval(pollInterval);
        resetUpdateButton();
        showStatusMessage('⏰ Timeout aggiornamento', 'warning');
    }, 900000);
}

// Eventi WebSocket per aggiornamento
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (window.pronosticiApp && window.pronosticiApp.socket) {
            // Aggiornamento avviato
            window.pronosticiApp.socket.on('aggiornamento_avviato', (data) => {
                console.log('🚀 WebSocket: Aggiornamento avviato', data);
                showStatusMessage(`🔄 ${data.message}`, 'warning');
            });
            
            // Aggiornamento completato
            window.pronosticiApp.socket.on('aggiornamento_completato', (data) => {
                console.log('📋 WebSocket: Aggiornamento completato', data);
                resetUpdateButton();
                
                if (data.success) {
                    showStatusMessage('🎉 Sistema aggiornato con successo!', 'success');
                    
                    // Ricarica le statistiche
                    if (window.pronosticiApp) {
                        window.pronosticiApp.loadStatistiche();
                    }
                } else {
                    showStatusMessage(`❌ Aggiornamento fallito: ${data.error}`, 'danger');
                }
            });
            
            console.log('🔄 Eventi WebSocket aggiornamento registrati');
        }
    }, 2000);
});

console.log('🔄 Sistema aggiornamento dati caricato');