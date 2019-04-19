function _bashRun($cmdString) {
    $acceptableExitCode = 0
    # This is unfortunately necessary because there is an interfacing issue between the windows console, windows containers, and MSYS2
    # Specifically, all of STDOUT and STDERR are lost when executing commands under those circumstances.
    cd "${env:TEMP}"
    $unixTemp = (& bash -c "pwd").Trim()
    _log "Executing BASH command '$cmdString' in working directory '$unixTemp'"
    $unixOut = "$unixTemp/bashRunOutput"
    $exec = "bash.exe"
    $arguments = ("-c", "'echo BASH COMMAND OUTPUT BEGINS >`"$unixOut`" && cd `"$unixTemp`" >>`"$unixOut`" 2>&1 && $cmdString >>`"$unixOut`" 2>&1 && echo BASH COMMAND OUTPUT EOF >>`"$unixOut`"'")
    $p = Start-Process -FilePath $exec -ArgumentList $arguments -Wait -PassThru
    cat "${myTemp}\bashRunOutput"
    _log "Process finished. Got exit code: $($p.ExitCode)"
    if($p.ExitCode -ne $acceptableExitCode) {
        _die "Expected ${acceptableExitCode}!"
    }
}
