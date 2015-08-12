var str = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function (data) {
    str += data;
});

process.stdin.on('end', function () {
    var postcss = require('postcss'),
        fmt = require('cssfmt'),
        formated;

    process.chdir(process.argv[2]);

    formated = postcss()
        .use(fmt())
        .process(str)
        .then(function (result) {
            process.stdout.write(result.css);
        })
        .catch(function (error) {
            process.stderr.write(error.toString());
        });
});
