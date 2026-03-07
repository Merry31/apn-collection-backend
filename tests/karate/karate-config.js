function fn() {
    var env = karate.env; // get system property 'karate.env'
    karate.log('karate.env system property was:', env);

    if (!env) {
        env = 'dev';
    }

    var config = {
        env: env,
        baseUrl: 'http://127.0.0.1:8081/api/v1'
    };

    // Set timeouts
    karate.configure('connectTimeout', 5000);
    karate.configure('readTimeout', 5000);

    return config;
}
