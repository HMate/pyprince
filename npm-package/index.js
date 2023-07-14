const path = require('node:path'); 

module.exports = class PyPrince {
    constructor() {
        this.executablePath = "";
    }
    static defaultExecutablePath = path.join(__dirname, "pyprince");
    static callPrince(...args) {
        // TODO: somehow put this whole call in a library, remove poetry dependency and hardcoded path
        return child_process
            .execFileSync("poetry", ["run", "python", "-m", "pyprince", ...args], { cwd: defaultExecutablePath })
            .toString();
        // TODO: Check result field 
    }

};