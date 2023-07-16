export class PyPrince {
  constructor(pythonExecutablePath?: string);
  callPrince(...args: string[]): string;
}
