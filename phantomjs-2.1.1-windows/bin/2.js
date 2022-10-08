
        var synth = window.speechSynthesis;
        console.log(synth)
        var voices = [];

        function populateVoiceList() {
            voices = synth.getVoices().sort(function (a, b) {
                const aname = a.name.toUpperCase(), bname = b.name.toUpperCase();
                if (aname < bname) return -1;
                else if (aname == bname) return 0;
                else return +1;
            });
            
        }

        populateVoiceList();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = populateVoiceList;
        }

        function speak() {
            if (synth.speaking) {
                console.error('speechSynthesis.speaking');
                return;
            }
            
            var txt ="请先输入要朗读的文本"; 
            var utterThis = new SpeechSynthesisUtterance(txt);
            utterThis.onend = function (event) {
                console.log('SpeechSynthesisUtterance.onend');
            }
            utterThis.onerror = function (event) {
                console.error('SpeechSynthesisUtterance.onerror');
            }
            
                    utterThis.voice = voices[0];
                    
            utterThis.pitch = pitch.value;
            utterThis.rate = rate.value;
            synth.speak(utterThis);
        }
 

        pitch.onchange = function () {
            pitchValue.textContent = pitch.value;
        }

        rate.onchange = function () {
            rateValue.textContent = rate.value;
        }

        volume.onchange = function () {
            volumeValue.textContent = volume.value;
        }

        voiceSelect.onchange = function () {
            speak();
        }
        speak();
