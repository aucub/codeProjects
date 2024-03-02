import { Ai } from './vendor/@cloudflare/ai.js';

export default {
    async fetch(request, env) {
        const { model, task } = parseRequest(request) || {};
        if (task === Task.TextGeneration) {
            return handleTextGeneration(request, env.AI, model);
        }
        return new Response('Task not supported', { status: 400 });
    }
};

const Task = {
    TextGeneration: 'text-generation',
};

function parseRequest(request) {
    const url = request.url;
    if (url.includes('chat/completions')) {
        const atIndex = url.indexOf('@');
        if (atIndex === -1) {
            return { model: request.json().model, task: Task.TextGeneration };
        }
        const paths = url.slice(atIndex).split('/');
        if (paths.length >= 3) {
            return { model: paths.slice(0, 3).join('/'), task: Task.TextGeneration };
        } else {
            return { model: paths.slice(0, paths.length).join('/'), task: Task.TextGeneration };
        }
    }
    return null;
}

async function handleTextGeneration(request, AI, model) {
    const ai = new Ai(AI);
    const chat = await request.json();
    const stream = chat.stream;
    const messages = chat.messages;
    const response = await ai.run(model, { messages, stream: stream });
    if (stream) {
        return new Response(transformReadableStream(response, model), {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        });
    } else {
        const formattedData = await formatResponse(response, model, false);
        return new Response(JSON.stringify(formattedData));
    }
}

async function formatResponse(data, model, stream) {
    if (stream) {
        return {
            id: `chatcmpl-${Date.now()}`,
            model: model,
            object: "chat.completion",
            created: Math.floor(Date.now() / 1000),
            choices: [
                {
                    index: 0,
                    delta: {
                        content: data.response,
                        role: "assistant"
                    },
                    finish_reason: "length"
                }
            ]
        };
    } else {
        return {
            id: `chatcmpl-${Date.now()}`,
            object: "chat.completion",
            created: Math.floor(Date.now() / 1000),
            model: model,
            choices: [
                {
                    index: 0,
                    message: {
                        content: data.response,
                        role: "assistant"
                    },
                    finish_reason: "length"
                }
            ]
        };
    }
}

function transformReadableStream(readableStream, model) {
    const decoder = new TextDecoder();
    const encoder = new TextEncoder();
    const transformStream = new TransformStream({
        async transform(chunk, controller) {
            let data = decoder.decode(chunk).replace(/^data: /, '').replace(/\n\n$/, '');
            if (data !== "[DONE]") {
                const formattedData = await formatResponse(JSON.parse(data), model, true)
                data = JSON.stringify(formattedData)
            }
            controller.enqueue(encoder.encode(`data: ${data}\n\n`));
        },
    });
    return readableStream.pipeThrough(transformStream);
}