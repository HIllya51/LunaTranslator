(function () {
    window.hasdone = false
    window.thistext = ''
    if (window.injectedjs) return
    window.injectedjs = true
    const originalFetch = window.fetch;
    window.fetch = function (url, init) {
        const fetchPromise = originalFetch.apply(this, arguments);
        if (!% s) return fetchPromise;
        window.hasdone = false;
        window.thistext = ''
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
                        if (line.substring(6) == '[DONE]') {
                            hasdone = true;
                            break;
                        }
                        try {
                            const chunk = JSON.parse(line.substring(6));
                                % s
                        } catch {

                        }
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
})() 