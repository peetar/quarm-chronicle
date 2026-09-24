/**
 * High-throughput asynchronous line generator that splits a byte stream
 * into lines without loading the whole file into memory.
 */
export async function* streamLines(stream: ReadableStream<Uint8Array>): AsyncGenerator<string, void, unknown> {
  const reader = stream.getReader();
  const decoder = new TextDecoder('utf-8', { fatal: false, ignoreBOM: true });
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        if (buffer.length > 0) {
          yield buffer;
        }
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      let lineStart = 0;
      let lineEnd = buffer.indexOf('\n');

      while (lineEnd !== -1) {
        let line = buffer.substring(lineStart, lineEnd);
        if (line.endsWith('\r')) {
          line = line.slice(0, -1);
        }
        yield line;

        lineStart = lineEnd + 1;
        lineEnd = buffer.indexOf('\n', lineStart);
      }

      buffer = buffer.substring(lineStart);
    }
  } finally {
    reader.releaseLock();
  }
}
