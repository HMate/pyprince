import * as fs from "fs";

export interface PyPrinceStats extends fs.Stats {
    filePath: string;
}

export class PyPrince {
  constructor(pythonExecutablePath?: string);
  callPrince(...args: string[]): string;
  async getPrinceInfo(): PyPrinceStats | Error;
}
