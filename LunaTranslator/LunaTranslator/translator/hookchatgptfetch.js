
const originalFetch = window.fetch;
var hasdone = true
var thistext = ''
window.fetch = function (input, init) {
    const fetchPromise = originalFetch.apply(this, arguments);
    if (!input.includes("conversation")) return fetchPromise;
    hasdone = false;
    thistext = ''
    // 构造一个自定义的可读流
    //controller.close()会导致真正的fetch被终止
    // 不太会js，只能让他假等待了，ui里面会显示在等待，但luna里面能读到，而且按钮也能正确按下
    const customReadableStream = new ReadableStream({
        start(controller) {
            setTimeout(() => {

                controller.close();
            }, 99999999999);

        },
    });
    fetchPromise.then(response => {
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('text/event-stream')) {
            console.log(response.body)
            const reader = response.body.getReader();

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
                        console.log("Chunk received:", chunk.message.content.parts[0]);
                        thistext = chunk.message.content.parts[0]
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

    return new Promise((resolve, reject) => {
        resolve(new Response(customReadableStream, {
            status: 200,
            headers: {
                'Content-type': 'text/event-stream'
            }
        }));

    });
};
