
const originalFetch = window.fetch;
var hasdone = true
var thistext = ''
window.fetch = function (input, init) {
    const fetchPromise = originalFetch.apply(this, arguments);
    if (!input.endsWith("completion/stream")) return fetchPromise;
    hasdone = false;
    thistext = ''
    fetchPromise.then(response => {
        const clone = response.clone()
        const contentType = clone.headers.get('content-type');
        if (contentType && contentType.includes('text/event-stream')) {
            const reader = clone.body.getReader();

            reader.read().then(function processStream({ done, value }) {

                if (done) {
                    hasdone = true;
                    return;
                }
                let lines = new TextDecoder('utf-8').decode(value); 
                lines = lines.split('\n')
                for (let i = 0; i < lines.length; i++) {
                    let line = lines[i]
                    line = line.trim()
                    if (line.length == 0) continue;
                     try {
                        const chunk = JSON.parse(line.substring(6)); 
                        if(chunk.event!='cmpl')continue;
                        console.log(chunk)
                        if(chunk.text)
                            thistext += chunk.text
                    } catch {  }
                }
                return reader.read().then(processStream);
            }).catch(error => {
                console.error('Error reading stream:', error);
            });
        }
    }).catch(error => {
        console.error('Fetch error:', error);
    });

    return fetchPromise;
};
