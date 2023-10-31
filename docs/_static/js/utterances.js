function addUtterances() {
    let script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://utteranc.es/client.js";
    script.async = "async";
    script.setAttribute("repo", "gaphor/gaphor-utterances");
    script.setAttribute("issue-term", "pathname");
    script.setAttribute("theme", "preferred-color-scheme");
    script.setAttribute("crossorigin", "anonymous");

    let bottomOfPage = document.querySelector("footer > .bottom-of-page");
    if (bottomOfPage) {
        bottomOfPage.parentNode.insertBefore(script, bottomOfPage);
    }
}

addUtterances();
