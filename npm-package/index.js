const path = require('node:path'); 

module.exports = class PyPrince {
    // By default we use the first one on PATH. TODO: Probably this is different on linux/windows..
    static defaultPythonPath = "python";

    constructor(pythonExecutablePath = PyPrince.defaultPythonPath) {
        this.pythonExecutablePath = pythonExecutablePath;
        this.pyprincePath = path.join(__dirname, "pyprince", "__main__.py");
    }

    static callPrince(...args) {
        // TODO: somehow put this whole call in a library, remove poetry dependency and hardcoded path
        return child_process
            .execFileSync(this.pythonExecutablePath, [this.pyprincePath, ...args])
            .toString();
        // TODO: Check result field 
    }

};