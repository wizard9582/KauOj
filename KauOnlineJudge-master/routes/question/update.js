const request = require('request')

const myRouter = require('../../lib/myRouter')

const router = myRouter.Router()

const bodyParser = require('body-parser')
router.use(bodyParser.json())

const multer = require('multer')

const _ = require('lodash')

const fs = require('fs')

router.get('/:id', (req, res) => {
    if (req.user === undefined) res.redirect('/login')
    else {
        request.get(`http://dofh.iptime.org:8000/api/problem/edit?id=${req.params.id}`, {
            headers: {
                'X-Csrftoken': req.user.csrftoken,
                Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
                'Content-Type': 'multipart/form-data'
            }
        }, (err, serverRes, body) => {
            body = JSON.parse(body)

            body.data.title = _.unescape(body.data.title)
            body.data.description = _.unescape(body.data.description)
            body.data.input_description = _.unescape(body.data.input_description)
            body.data.output_description = _.unescape(body.data.output_description)
            if (err || body.error) {
                console.error('err: ' + err)
                console.error('body.error: ' + body.data)
                res.redirect(`/question/${post._id}`)
                return
            } else {
                router.build = {
                    code: 200,
                    page: 'question/update',
                    message: 'question update',
                    param: {
                        title: 'Question Update',
                        data: body.data,
                        owner: req.user ? req.user.username === body.data.created_by.username : undefined
                    },
                }

                router.show(req, res)

                // TestCase 파일을 읽어오려고 했으나 표현이 불가능하다.
                // request.get(`http://dofh.iptime.org:8000/api/test_case?problem_id=${req.params.id}`, {
                //     headers: {
                //         'X-Csrftoken': req.user.csrftoken,
                //         Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
                //         'Content-Type': 'multipart/form-data'
                //     }
                // }, (err, serverRes, body) => {
                //     if (err || body.error) {
                //         console.error('err: ' + err)
                //         console.error('body.error: ' + body.data)
                //         res.redirect('/question')
                //     } else {
                //         router.build.param.data.test_case = body

                //         console.log(typeof(body))
                //         //각 페이지에 해당하는 내용을 완성했으면 log와 함께 페이지를 표시한다
                //         router.show(req, res)
                //     }
                // })
            }
        })
    }
})

// bodyParser: multipart/form-data 형식으로 입력받은 데이터를 json 형식으로 변환해준다.
// multer: multipart/form-data 형식으로 입력받은 파일을 저장해준다.
// 아래는 파일을 메모리에 저장해두고 나중에 POST의 formdata에 추가한다.
var storage = multer.memoryStorage()
var upload = multer({ storage })
router.post('/:id', upload.single('test_case_file'), (req, res) => {
    if (req.user === undefined) res.redirect('/login')

    //form에서 받아온 정보의 집합
    const post = req.body

    post.id = req.params.id

    //페이지에서 받아온 태그를 ','로 나눈 뒤 앞뒤 공백을 제거한다
    post.tags = post.tags.split(',')
    for (let i in post.tags) {
        post.tags[i] = post.tags[i].trim()
    }

    //페이지에서 받아온 언어 집합 ','로 나눈 뒤 앞뒤 공백을 제거한다
    /* post.languages = post.languages.split(',')
    for (let i in post.languages) {
        post.languages[i] = post.languages[i].trim()
    } */

    //추가할 문제를 풀 수 있는 언어 종류를 배열로 전송
    post.languages = []
    //가능한 언어를 post.languages에 삽입
    if (post['C'] === 'on') post.languages.push('C')
    if (post['C++'] === 'on') post.languages.push('C++')
    if (post['Java'] === 'on') post.languages.push('Java')
    if (post['Python2'] === 'on') post.languages.push('Python2')
    if (post['Python3'] === 'on') post.languages.push('Python3')
    //post[언어]는 백엔드 스키마에 없으므로 제거
    delete post['C']
    delete post['C++']
    delete post['Java']
    delete post['Python2']
    delete post['Python3']

    post.title = _.escape(post.title)
    post.description = _.escape(post.description)
    post.input_description = _.escape(post.input_description)
    post.output_description = _.escape(post.output_description)

    //추가할 문제의 예제를 객체의 배열로 전송
    //예제 입력의 배열과 예제 출력의 배열을 백엔드 스키마에 맞게 바꾼다
    post.samples = []
    if (post.input !== undefined) {
        if (typeof (post.input) === "string") {
            post.samples.push({ input: post.input, output: post.output })
        } else {
            for (i = 0; i < post.input.length; i++) {
                post.samples.push({
                    input: post.input[i],
                    output: post.output[i]
                })
            }
        }
    }
    // post.test_case_id = body.data.id
    //백엔드에서 사용하지 않는 변수는 제거
    /* post.input = undefined
    post.output = undefined */
    delete post.input
    delete post.output


    // 일부 변수들을 임의로 지정
    post.rule_type = "ACM"
    post.spj = false

    //체크박스의 on, off를 true, false로 변경
    post.share_submission = post.share_submission === 'on'
    post.visible = post.visible === 'on'


    //테스트케이스 추가
    var test_case_req = undefined
    if (req.file !== undefined) {
        test_case_req = request.post('http://dofh.iptime.org:8000/api/test_case', {
            headers: {
                'X-Csrftoken': req.user.csrftoken,
                Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
                'Content-Type': 'multipart/form-data'
            },
        }, (err, serverRes, body) => {
            if (err || body.error) {     //테스트케이스 추가 요청에 실패한 경우 
                console.error('err       : ' + err)
                console.error('body.data: ' + body.data)
                res.redirect(`/question/update/${post.id}`)
                return
            } else {
                console.log("테스트케이스")
                //데이터에 테스트케이스 추가
                body = JSON.parse(body)
                post.test_case_id = body.data.id
                post.test_case_score = [{ input_name: "1.in", output_name: "1.out", score: post.test_case_score }]

                //request로 전송할 문제 정보
                request.put({
                    uri: 'http://dofh.iptime.org:8000/api/problem/edit',
                    headers: {
                        'X-Csrftoken': req.user.csrftoken,
                        Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
                        'Content-Type': 'application/json'
                    },
                    json: post,
                }, (err, serverRes, body) => {
                    if (err || body.error) {     //문제 수정 요청에 실패한 경우 
                        console.error('err       : ' + err)
                        console.error('body.error: ' + body.error)

                        res.redirect(`/question/update/${post.id}`)
                    } else {
                        res.redirect('/question/' + post._id)
                    }
                })
            }
        })

        // formdata에 파일 추가
        var formData = test_case_req.form()
        formData.append('spj', "false")
        formData.append('file', req.file.buffer, {
            filename: '1.zip',
            contentType: 'application/zip'
        })
    } else {
        delete post.test_case_id

        if(post.test_case_score) post.test_case_score = [{ input_name: "1.in", output_name: "1.out", score: post.test_case_score }]
        else delete post.test_case_score

        //request로 전송할 문제 정보
        request.put({
            uri: 'http://dofh.iptime.org:8000/api/problem/edit',
            headers: {
                'X-Csrftoken': req.user.csrftoken,
                Cookie: `sessionid=${req.user.sessionid};csrftoken=${req.user.csrftoken};`,
                'Content-Type': 'application/json'
            },
            json: post,
        }, (err, serverRes, body) => {
            if (err || body.error) {     //문제 수정 요청에 실패한 경우 
                console.error('err       : ' + err)
                console.error('body.error: ' + body.error)

                res.redirect(`/question/update/${post.id}`)
            } else {
                res.redirect('/question/' + post._id)
            }
        })
    }


})

module.exports = router