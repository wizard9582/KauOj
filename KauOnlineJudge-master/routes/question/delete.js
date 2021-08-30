const request = require('request')

const myRouter = require('../../lib/myRouter')

const router = myRouter.Router()

router.post('/:id', (req, res) => {
    let id = req.params.id
    if (req.user === undefined) res.redirect('/question')
    else {
        request.delete(`http://dofh.iptime.org:8000/api/problem?id=${id}`, {
            headers: {
                'X-Csrftoken': req.user.csrftoken,
                Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
                'Content-Type': 'application/json'
            }
        }, (err, serverRes, body) => {
            body = JSON.parse(body)
            if (err || body.error) {
                console.error('err       : ' + err)
                console.error('body.error: ' + body.data)
                res.redirect(`/question`)
            } else {
                console.log(body)
                res.redirect(`/question`)
            }
        })
    }
})


module.exports = router