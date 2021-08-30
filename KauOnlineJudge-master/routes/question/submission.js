const request = require('request')

const myRouter = require('../../lib/myRouter')

const router = myRouter.Router()

router.get('/', (req, res) => {
    //사용자가 로그인하지 않았다면 이 페이지에 접근할 수 없으므로 /question으로 리다이렉트
    if (req.user === undefined) res.redirect('/question')

    let page = req.query.page || 0, limit = 10
    //request로 전송할 데이터 집합
    const submission = {
        uri: `http://dofh.iptime.org:8000/api/submissions?${page > 1 ? 'offset=' + (page-1) * limit : ''}&limit=${limit + 1}`,
        headers: {
            'X-Csrftoken': req.user.csrftoken,
            Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
            'Content-Type': 'application/json'
        }
    }

    //페이지의 쿼리 상태에 따라 uri에 여러 쿼리를 추가한다
    if (req.query.id)       submission.uri += `&problem_id=${req.query.id}`
    if (req.query.username) submission.uri += `&username=${req.query.username}`

    //request를 이용해 가져오고자 할 제출 목록 정보를 백엔드에 전송
    request.get(submission, (err, serverRes, body) => {
        if (err || body.error) {
            console.error('err:        ' + err)
            console.error('body.error: ' + body.data)
        } else {
            //백엔드로부터 받아온 정보를 json 형태로 파싱
            body = JSON.parse(body)
            
            router.build.page = 'question/submission'
            router.build.message = 'question/submission' 
                + ((req.query.id)       ? ` id=${req.query.id}`             : '') 
                + ((req.query.username) ? ` username=${req.query.username}` : '')
            router.build.param.title = `submission`
            router.build.param.results = body.data.results

            router.show(req, res)
        }
    })
})

// 파일 분리를 시도했으나 에러가 발생하여 부득이하게 이 파일에 삽입함
router.post('/:id', (req, res) => {
    let id = req.params.id
    //form에서 받아온 정보의 집합
    const post = req.body

    if (req.user === undefined) res.redirect('/login')

    //request로 전송할 문제풀이 정보
    const question_create = {
        uri: 'http://dofh.iptime.org:8000/api/submission',
        headers: {
            'X-Csrftoken': req.user.csrftoken,
            Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
            'Content-Type': 'application/json'
        },
        json: post
    }

    request.post(question_create, (err, serverRes, body) => {
        if (err || body.error) {
            console.error('err       : ' + err)
            console.error('body.error: ' + body.data)
            res.redirect(`/question/${id}`)
        } else {
            //제출한 문제의 id와 사용자 이름을 쿼리로 넘기면서 제출 목록을 확인
            // res.redirect(`/question/submission/${body.data.submission_id}`)
            res.redirect(`/question/submission?id=${id}&username=${req.user.username}`)
        }
    })
})

module.exports = router