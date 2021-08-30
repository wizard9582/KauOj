const fs = require('fs')

const myRouter = require('../lib/myRouter')

const router = myRouter.Router()

router.get('/', (req, res) => { //잘못 접근했을 경우 다른 페이지로 리다이렉트
    res.redirect('/')
})

/* router.get('/', (req, res) => { //잘못 접근했을 경우 다른 페이지로 리다이렉트
    req.session.redirect = 'user'
    if (req.user == undefined) res.redirect('/login')
    else res.redirect(`/user/${req.user.username}`)
})

router.get('/:id', (req, res) => {
    //위에서 설정한 redirect를 제거
    req.session.redirect = undefined

    //없는 유저의 유저 페이지를 확인하려 하면 에러 메세지를 출력해야 함
    if (!fs.readdirSync(__dirname + `/BE_test/users`).includes(`${req.params.id}.json`))
        res.redirect('/login')

    //사용자가 푼 문제들의 정보를 가져온 뒤
    let list = {}
    const user = JSON.parse(
        fs.readFileSync(__dirname + `/BE_test/users/${req.params.id}.json`)
    )

    //문제풀이 정보를 같은 결과끼리 모음
    for (q in user.submit) {
        if (list[user.submit[q]] == undefined) list[user.submit[q]] = []
        list[user.submit[q]].push(q)
    }

    router.build.param.list = list
    router.build.param.id = req.params.id

    //페이지 빌드
    router.build.param.title = `${req.params.id}의 정보`
    router.build.message = `${req.params.id} info`
    router.build.page = 'user'

    router.show(req, res)
}) */

module.exports = router