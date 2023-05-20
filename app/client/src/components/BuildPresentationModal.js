import React, {useEffect, useRef, useState} from 'react'
import './BuildPresentationModal.css'
import SelectFolderModal from "./SelectFolderModal";


const TemplateCard = (props) => {

    const ref = useRef()

    useEffect(() => {
        if (props.selectedTemplate === null || props.selectedTemplate.id !== props.template.id) {
            ref.current.classList.remove('selected')
        }
    }, [props.selectedTemplate])

    return (
        <img ref={ref} src={'data:image/png;base64,' + props.template.thumbnail} className='TemplateCard'
             onClick={() => {
                if (props.selectedTemplate && props.selectedTemplate.id === props.template.id) {
                    ref.current.classList.remove('selected')
                    props.setSelectedTemplate(null)
                } else {
                    ref.current.classList.add('selected')
                    props.setSelectedTemplate(props.template)
                }
        }}/>
    )

}

const BuildPresentationModal = (props) => {

    const [presName, setPresName] = useState('')
    const [saveTo, setSaveTo] = useState(null)
    const [selectedTemplate, setSelectedTemplate] = useState(null)

    const [styleTemplates, setStyleTemplates] = useState([])

    const [showSelectFolder, setShowSelectFolder] = useState(false)

    const BuildState = {
        CONSTRUCTING: 0,
        BUILD_WAIT: 1,
        BUILD_DONE: 2
    }

    const [buildState, setBuildState] = useState(BuildState.CONSTRUCTING)


    const [presentationRatio, setPresentationRatio] = useState('widescreen_16_to_9')

    useEffect(() => {
        if (props.showBuildPresentation)
            fetch('http://localhost:8000/presentations/generate-style-templates', {
                method: 'POST',
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({slides: props.previewSlides})
            }).then(res => res.json()).then(data => setStyleTemplates(data.templates))
    }, [props.showBuildPresentation])

    return (
        <div className='BuildPresentationModal' onClick={() => props.setShowBuildPresentation(false)}>
            <div className='build-presentation' onClick={e => e.stopPropagation()}>
                {(() => {
                    switch (buildState) {
                        case BuildState.CONSTRUCTING:
                            return <>
                                <h3>Имя презентации</h3>
                                <div className='pres-name'>
                                    <input type="text" value={presName} placeholder='Новая презентация'
                                           onChange={e => setPresName((e.target.value))}/>
                                </div>
                                <h3>Расположение</h3>
                                <div className='save-to'>
                                    <button onClick={() => setShowSelectFolder(true)}>
                                        {saveTo ? saveTo.name : 'Выбрать папку'}
                                    </button>
                                </div>
                                <h3>Стиль презентации</h3>
                                <div className='style-templates'>
                                    <div className={'style-templates-list'}>
                                        {styleTemplates.length > 0 ? styleTemplates.map(template =>
                                                <TemplateCard
                                                    template={template}
                                                    selectedTemplate={selectedTemplate}
                                                    setSelectedTemplate={setSelectedTemplate}/>) :
                                            <div className='loading'>Генерация стилей...</div>}
                                    </div>
                                </div>
                                <h3>Соотношение</h3>
                                <div className='ratio-filter'>
                                    <div className='radio-wrapper'>
                                        <div>
                                            <input id='ratio-filter-widescreen' type='radio' name='ratio-filter'
                                                   value='widescreen_16_to_9' defaultChecked
                                                   onChange={(e) => setPresentationRatio(e.target.value)}/>
                                            <label htmlFor='ratio-filter-widescreen'>Широкоформатный 16:9</label>
                                        </div>
                                        <div>
                                            <input id='ratio-filter-standard' type='radio' name='ratio-filter'
                                                   value='standard_4_to_3'
                                                   onChange={(e) => setPresentationRatio(e.target.value)}/>
                                            <label htmlFor='ratio-filter-standard'>Стандартный 4:3</label>
                                        </div>
                                    </div>
                                </div>
                                <button onClick={() => {
                                    setBuildState(BuildState.BUILD_WAIT)
                                    console.log(presName)
                                    fetch('http://localhost:8000/presentations/build', {
                                        method: 'POST',
                                        credentials: "include",
                                        headers: {
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify({
                                            name: presName.length > 0 ? presName : 'New presentation',
                                            save_to: saveTo ? saveTo.id : null,
                                            style_template: selectedTemplate ? selectedTemplate.id : null,
                                            ratio: presentationRatio,
                                            slides: props.previewSlides
                                        })
                                    }).then(() => setBuildState(BuildState.BUILD_DONE))
                                }}>
                                    Собрать презентацию
                                </button>
                            </>
                        case BuildState.BUILD_WAIT:
                            return <div className='loading'>Сборка презентации...</div>
                        case BuildState.BUILD_DONE:
                            return <div className='build-done-consent'>
                                <h3>Сборка презентации завершена</h3>
                                <div>
                                    <button onClick={() => {
                                    fetch('http://localhost:8000/presentations/get-built-presentation?' +
                                        new URLSearchParams({pres_name: presName.length > 0 ? presName : 'New presentation'}), {
                                            credentials: "include"
                                        })
                                        .then(res => res.blob())
                                        .then(blob => {
                                            const blobURL = window.URL.createObjectURL(blob)
                                            const a = document.createElement('a')
                                            a.href = blobURL
                                            a.download = presName.length > 0 ? presName : 'New presentation'
                                            a.click()
                                            a.remove()
                                            window.URL.revokeObjectURL(blobURL)
                                        })
                                        .then(() => {
                                            fetch('http://localhost:8000/presentations/clear-built', {
                                                method: "POST",
                                                credentials: "include"
                                            }).then(props.setShowBuildPresentation(false))
                                        })
                                    }}>Скачать</button>
                                    <button onClick={() => {
                                        fetch('http://localhost:8000/presentations/clear-built', {
                                                method: "POST",
                                                credentials: "include"
                                        }).then(props.setShowBuildPresentation(false))
                                    }}>
                                        Пропустить
                                    </button>
                                </div>

                            </div>
                    }
                })()}

            </div>
            {showSelectFolder ?
                <SelectFolderModal
                    userFileTree={props.userFileTree}
                    setShowSelectFolder={setShowSelectFolder}
                    setSaveTo={setSaveTo}
                /> : null
            }

        </div>


    )
}


export default BuildPresentationModal