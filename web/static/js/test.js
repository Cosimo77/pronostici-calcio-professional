// Script di test per verificare l'interfaccia web
console.log("=== Test Sistema Predizioni ===");

// Test 1: Verifica che gli elementi esistano
console.log("1. Verifica elementi DOM:");
const squadraCasa = document.getElementById('squadra-casa');
const squadraTrasferta = document.getElementById('squadra-trasferta');
const form = document.getElementById('predizione-form');
const risultato = document.getElementById('risultato-predizione');

console.log('- squadra-casa:', squadraCasa ? '✅' : '❌');
console.log('- squadra-trasferta:', squadraTrasferta ? '✅' : '❌');
console.log('- predizione-form:', form ? '✅' : '❌');
console.log('- risultato-predizione:', risultato ? '✅' : '❌');

// Test 2: Verifica che le squadre siano caricate
console.log("\n2. Verifica squadre caricate:");
if (squadraCasa && squadraTrasferta) {
    console.log('- Opzioni squadra casa:', squadraCasa.options.length);
    console.log('- Opzioni squadra trasferta:', squadraTrasferta.options.length);
}

// Test 3: Test API manuale
console.log("\n3. Test API predizione:");
async function testAPI() {
    try {
        const response = await fetch('/api/predici', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                squadra_casa: 'Inter',
                squadra_ospite: 'Juventus'
            })
        });
        
        const data = await response.json();
        console.log('Risposta API:', data);
        return data;
    } catch (error) {
        console.error('Errore API:', error);
    }
}

// Test 4: Simula riempimento form e submit
console.log("\n4. Test simulazione form:");
function simulaPredizione() {
    if (squadraCasa && squadraTrasferta && form) {
        // Imposta valori
        squadraCasa.value = 'Inter';
        squadraTrasferta.value = 'Juventus';
        
        console.log('Valori impostati');
        console.log('- Casa:', squadraCasa.value);
        console.log('- Trasferta:', squadraTrasferta.value);
        
        // Simula submit
        console.log('Simulazione submit...');
        if (window.pronosticiApp) {
            window.pronosticiApp.makePrediction();
        } else {
            console.log('App non trovata, submit manuale...');
            form.dispatchEvent(new Event('submit'));
        }
    }
}

// Esegui test
testAPI().then(() => {
    console.log("\n=== Test completati ===");
    console.log("Per testare il form, esegui: simulaPredizione()");
});

// Rendi disponibile la funzione di test
window.testPredizioni = {
    simulaPredizione,
    testAPI
};