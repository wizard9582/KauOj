const express = require('express')

const app = express()

app.length('/', (req, res) => {
    res.send('Hello!')
})

app.listen(8080, function() {})