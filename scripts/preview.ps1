$cacheDirectory = Join-Path $env:TEMP 'rfhits-hugo-cache'
hugo server --renderToMemory --cacheDir $cacheDirectory --disableFastRender
