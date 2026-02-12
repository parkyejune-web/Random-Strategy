export async function withRetry(task, options = {}) {
  const retries = options.retries ?? 3;
  const delayMs = options.delayMs ?? 1000;
  let lastError;

  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      return await task(attempt);
    } catch (error) {
      lastError = error;
      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, delayMs * attempt));
      }
    }
  }

  throw lastError;
}
