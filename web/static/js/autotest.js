// Test automatico per l'interfaccia web
console.log('🧪 AVVIO TEST AUTOMATICO...');

// Aspetta che l'app sia completamente inizializzata
function waitForApp() {
    if (typeof window.pronosticiApp !== 'undefined' && window.pronosticiApp) {
        runTests();
    } else {
        setTimeout(waitForApp, 500);
    }
}

function runTests() {
    console.log('🔍 Test elementi DOM...');
    
    // Verifica elementi
    const casaSelect = document.getElementById('squadra-casa');
    const ospiteSelect = document.getElementById('squadra-trasferta');
    const form = document.getElementById('predizione-form');
    const risultato = document.getElementById('risultato-predizione');
    
    console.log('📋 VERIFICA ELEMENTI:');
    console.log('- squadra-casa:', casaSelect ? '✅' : '❌');
    console.log('- squadra-trasferta:', ospiteSelect ? '✅' : '❌');
    console.log('- predizione-form:', form ? '✅' : '❌');
    console.log('- risultato-predizione:', risultato ? '✅' : '❌');
    
    if (!casaSelect || !ospiteSelect) {
        console.error('❌ ELEMENTI MANCANTI!');
        return;
    }
    
    // Verifica squadre caricate
    console.log('📊 SQUADRE DISPONIBILI:');
    console.log('- Casa:', casaSelect.options.length, 'opzioni');
    console.log('- Trasferta:', ospiteSelect.options.length, 'opzioni');
    
    if (casaSelect.options.length > 2) {
        console.log('🏟️ Prime squadre disponibili:');
        for (let i = 1; i < Math.min(4, casaSelect.options.length); i++) {
            console.log(`  ${i}: ${casaSelect.options[i].value}`);
        }
        
        // Test predizione automatica
        console.log('🚀 AVVIO TEST PREDIZIONE...');
        
        // Seleziona squadre
        casaSelect.value = casaSelect.options[1].value; // Prima squadra
        ospiteSelect.value = ospiteSelect.options[2].value; // Seconda squadra
        
        console.log(`🏆 Test: ${casaSelect.value} vs ${ospiteSelect.value}`);
        
        // Chiama funzione predizione sull'istanza, non sulla classe
        if (window.pronosticiApp) {
            setTimeout(() => {
                console.log('🔮 Chiamata makePrediction...');
                window.pronosticiApp.makePrediction();
            }, 1000);
        } else {
            console.error('❌ Istanza PronosticiApp non disponibile!');
        }
    } else {
        console.error('❌ Nessuna squadra caricata!');
    }
}

// Avvia il test quando la pagina è caricata
setTimeout(waitForApp, 1000);
console.log('⏳ Test avviato, attendi inizializzazione app...');