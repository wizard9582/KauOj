const request = require('request')

const myRouter = require('../lib/myRouter')

const router = myRouter.Router()

const _ = require('lodash')

// 문제 리스트, 문제 생성, 문제 제출 화면은 라우팅을 이용해 다른 파일에 정의
router.use('/', require('./question/list'))
router.use('/create', require('./question/create'))
router.use('/delete', require('./question/delete'))
router.use('/update', require('./question/update'))
router.use('/recommend', require('./question/recommend'))
router.use('/submission', require('./question/submission'))
//router.use('/:id',          require('./question/question'))


router.get('/:id', (req, res) => {  // 한 문제의 정보 및 해답 제출란
    let id = req.params.id
    router.build.message = `question id: ${id}`

    request.get({
        uri: `http://dofh.iptime.org:8000/api/problem?problem_id=${id}`
    }, (err, serverRes, body) => {
        body = JSON.parse(body)

        body.data.description = _.unescape(body.data.description)
        body.data.input_description = _.unescape(body.data.input_description)
        body.data.output_description = _.unescape(body.data.output_description)
        if (err || body.error) {
            console.error('err: ' + err)
            console.error('body.error: ' + body.data)
            res.redirect('/question')
        } else {
            try {
                // 문제 정보를 question.pug에 넘겨 문제 페이지를 생성
                router.build.page = 'question'
                router.build.param.title = `${id}. ${body.data.title}`
                router.build.param.q = body.data
                router.build.param.owner = req.user ? req.user.username === body.data.created_by.username : undefined
                // router.build.param.submit = ''/* router.submit[_id] */
            } catch (err) { // 문제 페이지가 없는 경우
                console.error(err)
                router.build.code = 404;
                router.build.param.title = 'Question id Error'
                router.build.message += ' not found'
            }

            //각 페이지에 해당하는 내용을 완성했으면 log와 함께 페이지를 표시한다
            router.show(req, res)
        }
    })
})


module.exports = router