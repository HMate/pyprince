import * as fs from "fs";

export class PyPrince {
  constructor(pythonExecutablePath?: string);
  callPrince(...args: string[]): string;
  async getPrinceInfo(): fs.Stats | Error;
}
