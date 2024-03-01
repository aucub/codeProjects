export default {
    async fetch(request) {
        const url = new URL(request.url);
        const path = url.pathname.split('/forward/')[1];

        if (path && path.includes('ai/run') && path.includes('v1/chat/completions')) {
            let redirectUrl = `https://${path.replace('v1/chat/completions', '')}`;
            redirectUrl = redirectUrl.replace(/\/$/, '');

            let requestBody = await request.text();
            let shouldStream = true;

            if (requestBody) {
                requestBody = JSON.parse(requestBody);
                shouldStream = requestBody.stream;
                requestBody.stream = false;
            }

            const redirectRequest = new Request(redirectUrl, {
                method: request.method,
                headers: request.headers,
                body: requestBody ? JSON.stringify(requestBody) : null
            });

            try {
                const redirectResponse = await fetch(redirectRequest);

                if (!redirectResponse.ok) {
                    return redirectResponse;
                }

                const data = await redirectResponse.json();

                const modelName = url.pathname.split('/').pop();

                if (shouldStream) {

                    let { readable, writable } = new TransformStream();
                    streamResponse(writable, data, modelName, true);

                    return new Response(readable, {
                        headers: {
                            'Content-Type': 'text/event-stream',
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive'
                        }
                    });

                } else {
                    const modified = formatResponse(data, modelName, false);
                    return new Response(JSON.stringify(modified), {
                        headers: { 'Content-Type': 'application/json' }
                    });

                }
            } catch (e) {
                return new Response('Failed to fetch the API', { status: 500 });
            }
        }

        return new Response('No path specified', { status: 400 });
    }
}

async function streamResponse(writable, data, modelName, stream) {
    const encoder = new TextEncoder();
    const writer = writable.getWriter();
    try {
        let modified = formatResponse(data, modelName, stream);
        let modifiedChunk = encoder.encode("data: " + JSON.stringify(modified) + '\n\n');
        await writer.write(modifiedChunk);
    } finally {
        writer.close();
    }
}

function formatResponse(data, modelName, stream) {
    if (stream) return {
        id: `chatcmpl-${Date.now()}`,
        object: "chat.completion",
        created: Math.floor(Date.now() / 1000),
        model: modelName,
        choices: [
            {
                index: 0,
                delta: {
                    content: data?.result?.response?.trim(),
                    role: "assistant"
                },
                finish_reason: "length"
            }
        ]
    }
    else return {
        id: `chatcmpl-${Date.now()}`,
        object: "chat.completion",
        created: Math.floor(Date.now() / 1000),
        model: modelName,
        choices: [
            {
                index: 0,
                message: {
                    content: data?.result?.response?.trim(),
                    role: "assistant"
                },
                finish_reason: "length"
            }
        ]
    }
}
