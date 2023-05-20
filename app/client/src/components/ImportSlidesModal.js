import React, {useEffect, useRef, useState} from 'react'
import './ImportSlidesModal.css'

const Presentation = (props) => {

    const ref = useRef()

    useEffect(() => {
        ref.current.checked = props.checkAll
        if (props.checkAll) {
            props.setSelectedPresentations(prev => [...prev, props.presentation])
        } else {
            props.setSelectedPresentations(prev => prev.filter(pres => pres.id !== props.presentation.id))
        }
    }, [props.checkAll])

    return (
        <div className='Presentation'>
            <input ref={ref} id={'pres-' + props.presentation.id} type='checkbox' onChange={
                (e) => {
                    if (e.currentTarget.checked) {
                        props.setSelectedPresentations(prev => [...prev, props.presentation])
                    } else {
                        props.setSelectedPresentations(prev => prev.filter(pres => pres.id !== props.presentation.id))
                    }

                }
            }/>
            <label htmlFor={'pres-' + props.presentation.id}>{props.presentation.name}</label>
        </div>
    )
}


const ImportSlidesModal = (props) => {

    const [presentations, setPresentations] = useState([])

    const [checkAll, setCheckAll] = useState(true)

    const [selectedPresentations, setSelectedPresentations] = useState([])
    const [tagQuery, setTagQuery] = useState('')
    const [searchPhrase, setSearchPhrase] = useState('')
    const [slideRatio, setSlideRatio] = useState('auto')

    useEffect(() => {

        if (props.userFileTree) {
            const presArr = []
            const traverse = (node) => {
                if (node.type === 'presentation') {
                    presArr.push(node)
                } else if (node.type === 'folder' && node.mark) {
                    node.children.map(child => traverse(child))
                }
            }

            traverse(props.userFileTree)
            setPresentations(presArr)
        }

    }, [props.userFileTree])


    return (
        <div className='ImportSlidesModal' onClick={() => props.setShowImportSlides(false)}>
            <div className='import-slides' onClick={e => e.stopPropagation()}>
                <div className='presentation-filter'>
                    <h3>Презентации</h3>
                    {presentations.length > 0 ?
                        <>
                         <div className='presentation-list'>
                            {presentations.map(
                                pres => <Presentation
                                    checkAll={checkAll}
                                    presentation={pres}
                                    setSelectedPresentations={setSelectedPresentations}/>
                            )}
                         </div>
                        <button onClick={() => setCheckAll(prev => !prev)}>
                            {checkAll ? 'Снять выделение' : 'Выбрать все'}
                         </button>
                        </>
                        : <div className='loading'>Загрузка...</div>}


                </div>
                <div className='tag-filter'>
                    <h3>Теги</h3>
                    <input type="text" value={tagQuery} placeholder='tag1 > 100'
                           onChange={(e) => {
                        setTagQuery(e.target.value)
                    }}/>
                </div>
                <div className='text-filter'>
                    <h3>Текст</h3>
                    <input type="text" value={searchPhrase} placeholder='Текст слайда'
                           onChange={(e) => {
                        setSearchPhrase(e.target.value)
                    }}/>
                </div>
                <div className='ratio-filter'>
                    <h3>Соотношение</h3>
                    <div className='radio-wrapper'>
                        <div>
                            <input id='ratio-filter-auto' type='radio' name='ratio-filter' value='auto' defaultChecked
                                   onChange={(e) => setSlideRatio(e.target.value)}/>
                            <label htmlFor='ratio-filter-auto'>Авто</label>
                        </div>
                        <div>
                            <input id='ratio-filter-widescreen' type='radio' name='ratio-filter'
                                   value='widescreen_16_to_9'
                                   onChange={(e) => setSlideRatio(e.target.value)}/>
                            <label htmlFor='ratio-filter-widescreen'>Широкоформатный 16:9</label>
                        </div>
                        <div>
                            <input id='ratio-filter-standard' type='radio' name='ratio-filter'
                                   value='standard_4_to_3'
                                   onChange={(e) => setSlideRatio(e.target.value)}/>
                            <label htmlFor='ratio-filter-standard'>Стандартный 4:3</label>
                        </div>
                    </div>
                </div>
                <button onClick={() => {
                    props.setSelectedPoolSlides([])
                    fetch('http://localhost:8000/slides/by-filters', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            presentations: selectedPresentations,
                            tag_query: tagQuery,
                            text_phrase: searchPhrase,
                            ratio: slideRatio
                        }),
                        credentials: "include"
                    }).then(res => res.json()).then(data => props.setPoolSlides(data.slides))
                    props.setShowImportSlides(false)
                }}>Импорт слайдов</button>
            </div>
        </div>
    )
}

export default ImportSlidesModal