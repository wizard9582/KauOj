const request = require('request')

const myRouter = require('../../lib/myRouter')

const router = myRouter.Router()

router.get('/', (req, res) => {
    //페이지에 표시할 문제의 집합을 배열로 저장
    let q_list = []

    request.get({ 
        uri: 'https://d7lp6qa3l9.execute-api.ap-northeast-2.amazonaws.com/kauoj_recommend'
    }, (err, serverRes, body) => {
        //백엔드로부터 받아온 정보를 json 형태로 파싱
        body = JSON.parse(body)

        if (err || body.error) {
            console.error('err:        ' + err)
            console.error('body.error: ' + body.error)
            res.redirect('/')
        } else {
            body.QUIZ.forEach(q => {
                request.get({
                    uri: `http://dofh.iptime.org:8000/api/problem?problem_id=${q}`
                }, (q_err, q_serverRes, q_body) => {
                    q_body = JSON.parse(q_body)

                    let q_item = {}
                    
                    if (q_err || q_body.error) {
                        q_item._id = q,
                        q_item.title = '',
                        q_item.tags = [''],
                        q_item.languages = ['']
                    } else {
                        q_item._id = q,
                        q_item.title = q_body.data.title,
                        q_item.tags = q_body.data.tags,
                        q_item.languages = q_body.data.languages
                    }

                    q_list.push(q_item)

                    if (q_list.length == body.QUIZ.length) {
                        router.build.page = 'question/recommend'
                        router.build.message = 'recommended question list'
        
                        router.build.param.q_list = q_list
                        router.build.param.page = 0
                        router.build.param.len = q_list.length
                        router.show(req, res)
                    }
                })
            })
        }
    })
})

module.exports = router