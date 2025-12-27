'use strict';

const path = require("node:path"); 
const fs = require("node:fs"); 
const { execFileSync } = require("node:child_process");

class PyPrince {
    // By default we use the first one on PATH. TODO: Probably this is different on linux/windows..
    static defaultPythonPath = "python";

    constructor(pythonExecutablePath = PyPrince.defaultPythonPath) {
        this.pythonExecutablePath = pythonExecutablePath;
        this.pyprincePath = path.join(__dirname, "pyprince.pyz");
    }

    callPrince(...args) {
        return execFileSync(this.pythonExecutablePath, [this.pyprincePath, ...args]).toString();
        // TODO: Check result field 
    }

    async getPrinceInfo() {
        try {
            const stats = await fs.promises.stat(this.pyprincePath);
            stats.filePath = this.pyprincePath;
            return stats;
        } catch (err) {
            throw err;
        }
    }
};

module.exports = { PyPrince };