import FolderList from "./folder-list.js";
import PresentationDrawer from "./presentation-drawer.js";
import SlideTagsList from "./slide-tags-list.js";
import SmallDropList from "./small-drop-list.js";

const slideTagsList = new SlideTagsList(
    document.querySelector('#slideTagsDropList'),
    (tag) => {

    })

const updateSlideTags = async (slide) => {
    console.log(slide)
    const slideTags = await fetch(`http://localhost:8000/links/slide-tags?slide_id=${slide.id}`)
        .then(res => res.json())
    slideTagsList.loadList(slide, slideTags, updateSlideTags)
}

const presDrawer = new PresentationDrawer(
    document.querySelector('.pres-drawer'),
    updateSlideTags
)

const folderList = new FolderList(
    document.querySelector('#folderDropList'),
    (pres, slides) => {
        hideSlidesSourcesModal()
        presDrawer.draw(slides)
        document.querySelector('.pres-drawer-header').innerHTML = `${pres.name}`
    })

const folderPresList = await fetch('http://localhost:8000/presentations/folders-test').then(res => res.json())
folderList.loadList(folderPresList)




const slidesSourcesModal = document.querySelector('.slides-sources-modal')
const logicalExpressionInput = slidesSourcesModal.querySelector('#logicalExpressionInput')
const selectedSlides = slidesSourcesModal.querySelector('.selected-slides-window')
let selectedSlidesObject = null
const destRoute = slidesSourcesModal.querySelector('.dest-route-window')
const confirmImportBtn = slidesSourcesModal.querySelector('#confirmImportBtn')
const cancelImportBtn = slidesSourcesModal.querySelector('#cancelImportBtn')


document.querySelector('.import-slides-button').addEventListener('click', () => {
    document.querySelector('.pres-drawer-header').style.display = 'none'
    document.querySelector('.pres-drawer').style.display = 'none'
    document.querySelector('.import-slides-button').style.display = 'none'
    slidesSourcesModal.classList.add('visible')
})

const presImportList = new SmallDropList(
        document.querySelector('#importPresList'),
        console.log
    )


const folderImportList = new SmallDropList(
    document.querySelector('#importFolderList'),
    (folder) => {

        presImportList.loadList(
            [
                ...folder.presentations,
                {
                    'name': 'Новая презентация.pptx',
                }
            ])
    }
)

folderImportList.loadList(folderPresList, 'name')

function hideSlidesSourcesModal() {
    logicalExpressionInput.value = ''
    selectedSlides.innerHTML = ''

    document.querySelector('.pres-drawer-header').style.display = 'flex'
    document.querySelector('.pres-drawer').style.display = 'flex'
    document.querySelector('.import-slides-button').style.display = 'flex'

    slidesSourcesModal.classList.remove('visible')


}

cancelImportBtn.addEventListener('click', () => {
    hideSlidesSourcesModal()
})

confirmImportBtn.addEventListener('click', async () => {
    selectedSlidesObject.forEach((element, index) => {
        selectedSlidesObject[index] = {
            id: element.id,
            slides: element.slides.map(slide => slide.index)
        }
    })
    const loadingElement = document.createElement('div')
    loadingElement.classList.add('lds-dual-ring')
    document.querySelector('.pres-drawer').appendChild(loadingElement)
    document.querySelector('.lds-dual-ring').style.display = 'inline-block'
    await fetch('http://localhost:8000/presentations/build', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: presImportList.input.value,
            id: presImportList.selectedElement.id,
            body: selectedSlidesObject})
    })
    hideSlidesSourcesModal()
    const folderPresList = await fetch('http://localhost:8000/presentations/folders-test').then(res => res.json())
    folderList.loadList(folderPresList)
    presDrawer.drawerElement.innerHTML = ''
    document.querySelector('.lds-dual-ring').style.display = 'none'
})

logicalExpressionInput.addEventListener('input', async () => {

    selectedSlidesObject = await fetch(
        `http://localhost:8000/presentations/slides-by-query?query=${logicalExpressionInput.value}`
    ).then(res => res.json())

    selectedSlides.innerHTML = ''
    let slidesCount = 0
    for (const pres of selectedSlidesObject) {
        const presBox = document.createElement('div')
        presBox.classList.add('presBox')

        const presBoxHeader = document.createElement('div')
        presBoxHeader.classList.add('presBoxHeader')
        presBoxHeader.innerHTML = `Презентация: "${pres.name}"`
        presBox.appendChild(presBoxHeader)

        const presBoxContent = document.createElement('div')
        presBoxContent.classList.add('presBoxContent')
        presBox.appendChild(presBoxContent)

        for (const slide of pres.slides) {
            const img = document.createElement('img')
            img.src = 'data:image/png;base64,' + slide.thumbnail
            img.classList.add('slidesImportImage')
            presBoxContent.appendChild(img)
            slidesCount++
        }
        selectedSlides.appendChild(presBox)
    }
    destRoute.querySelector('.slides-text').innerHTML = `Слайды (${slidesCount}) →`

})