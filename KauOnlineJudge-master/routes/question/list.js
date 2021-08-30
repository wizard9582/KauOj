const fs = require('fs')
const request = require('request')

const myRouter = require('../../lib/myRouter')

const router = myRouter.Router()

router.get('/', (req, res) => {
    //페이지에 표시할 문제의 집합을 배열로 저장
    let page = req.query.page || 0, limit = 10
    let q_list = []

    request.get({ 
        uri: `http://dofh.iptime.org:8000/api/problem?${page > 1 ? 'offset=' + (page-1) * limit : ''}&limit=${limit + 1}`
    }, (err, serverRes, body) => {
        //백엔드로부터 받아온 정보를 json 형태로 파싱
        body = JSON.parse(body)

        if (err || body.error) {
            console.error('err:        ' + err)
            console.error('body.error: ' + body.error)
            res.redirect('/')
        } else {
            //백엔드에서 받아온 문제 정보들 중 필요한 것만 가져옴
            let hasNext = false
            body.data.results.forEach((q, i) => {
                if ( (req.query.tag !== undefined) && !(q.tags.includes(req.query.tag)) ) return
                if (i == 10) {
                    hasNext = true
                } else{
                    q_list.push({
                        _id: q._id,
                        title: q.title,
                        tags: q.tags,
                        languages: q.languages,
                    })
                }
                
            })
    
            router.build.page = 'question/list'
            router.build.message = 'question list'
            if (req.query.tag != undefined) 
                router.build.message += `: ${req.query.tag}`
        
            router.build.param.q_list = q_list
            router.build.param.page = page
            router.build.param.hasNext = hasNext
            router.show(req, res)
        }
    })
})

module.exports = router