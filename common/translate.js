const translate = require('google-translate-api');

arg = process.argv.slice(3);
opt = {}
opt.from = arg[0];
opt.to   = arg[1];

translate(process.argv[2], opt).then(res => {
    console.log(res.text);
    //=> I speak English
    console.log(res.from.language.iso);
    //=> nl
}).catch(err => {
    console.error(err);
});
