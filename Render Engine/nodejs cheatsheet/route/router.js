function route(pathname) {
    if (pathname == '/upload')
        console.log("Upload Page not ready")
    console.log("About to route a request for " + pathname);
}
exports.route = route;