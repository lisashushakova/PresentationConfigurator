import {route} from "./script.js";

export default class FilesTreeList {
    constructor(htmlContainer, drawerCallback) {
        this.header = htmlContainer.querySelector('.ftl-header')
        this.searchField = this.header.querySelector('.ftl-search-field')
        this.searchField.addEventListener('input', () => {
            this.search(this.fileTree, this.searchField.value)
        })

        this.body = htmlContainer.querySelector('.ftl-body')

        this.selectedPres = null

        this.drawerCallback = drawerCallback
    }

    init(fileTree) {
        this.selectedPres = null
        this.fileTree = fileTree
        this.body.innerHTML = ''
        for (const root of fileTree) {
            const rootHTML = document.createElement('div')
            this.body.appendChild(rootHTML)
            rootHTML.classList.add('ftl-root')
            rootHTML.innerHTML = root.name

            rootHTML.addEventListener('click', () => {
                rootHTML.visible = !rootHTML.visible
                for (const child of rootHTML.children) {
                    if (rootHTML.visible) {
                        child.classList.remove('hidden')
                    } else {
                        child.classList.add('hidden')
                    }
                }
            })

            root.html = rootHTML

            for (const rootChild of root.children) {
                this.traverseAndBuild(root, rootHTML, rootChild)
            }
        }
    }

    updateSyncStatus(statusList) {
        for (const root of this.fileTree) {
            this.traverseAndUpdateStatus(root, statusList)
        }
    }

    traverseAndUpdateStatus(node, statusList) {
        if (node.type === 'pres') {
            if (statusList[node.id] === 'creating') {
                node.html.locked = true
                node.html.classList.add('locked')
                node.html.classList.add('syncing-created')
            } else if (statusList[node.id] === 'updating') {
                node.html.locked = true
                node.html.classList.add('locked')
                node.html.classList.add('syncing-updated')
            } else {
                node.html.locked = false
                node.html.classList.remove('locked')
                node.html.classList.remove('syncing-created')
                node.html.classList.remove('syncing-updated')
            }
        }
        else {
            if (node.hasOwnProperty('children')) {
                for (const child of node.children) {
                    this.traverseAndUpdateStatus(child, statusList)
                }
            }
        }
    }

    traverseAndBuild(parent, parentHTML, child) {
        const childHTML = document.createElement('div')
        parentHTML.appendChild(childHTML)
        childHTML.innerHTML = child.name

        child.html = childHTML

        if (child.type === "pres") {
            childHTML.classList.add('ftl-pres')
            childHTML.selected = false
            childHTML.locked = true
            childHTML.classList.add('locked')
            childHTML.addEventListener('click', async (e) => {
                e.stopPropagation()
                if (!childHTML.locked) {
                    const mainPresColumnHeader = document.querySelector('.main-pres-column-header')
                    childHTML.selected = !childHTML.selected
                    if (childHTML.selected) {
                        if (this.selectedPres != null) {
                            this.selectedPres.html.selected = false
                            this.selectedPres.html.classList.remove('selected')
                        }


                        this.selectedPres = child
                        childHTML.classList.add('selected')

                        mainPresColumnHeader.innerHTML = child.name

                        const selectedPresSlides = await fetch(route + 'slides/by-pres-id?' + new URLSearchParams({
                            pres_id: this.selectedPres.id
                        })).then(res => res.json())
                        await this.drawerCallback(selectedPresSlides)
                    } else {
                        this.selectedPres = null
                        childHTML.classList.remove('selected')

                        mainPresColumnHeader.innerHTML = 'Название презентации'

                        await this.drawerCallback(null)

                    }
                }
            })
            const loadingMark = document.createElement('div')
            loadingMark.classList.add('ftl-loading-mark')
            childHTML.appendChild(loadingMark)

        } else {
            childHTML.classList.add('ftl-folder')
            childHTML.visible = true

            childHTML.addEventListener('click', (e) => {
                childHTML.visible = !childHTML.visible
                for (const childChild of childHTML.children) {
                    if (childHTML.visible) {
                        childChild.classList.remove('hidden')
                    } else {
                        childChild.classList.add('hidden')
                    }
                }
                e.stopPropagation()
            })

            for (const childChild of child.children) {
                this.traverseAndBuild(child, childHTML, childChild)
            }
        }
    }


    traverseAndShow(node) {
        node.html.classList.remove('hidden')
        if (node.hasOwnProperty('children')) {
            for (const child of node.children) {
                this.traverseAndShow(child)
            }
        }
    }

    search(fileTree, searchPhrase) {
        for (const root of this.fileTree) {
            this.traverseAndShow(root)
        }
        for (const root of this.fileTree) {
            this.traverseAndSearch(root, searchPhrase)
        }
    }

    traverseAndSearch(node, searchPhrase) {
        if (node.name.includes(searchPhrase)) {
            node.html.classList.remove('hidden')
            return true
        } else if (node.hasOwnProperty('children')) {
            const traverseResult = node.children.map(child => this.traverseAndSearch(child, searchPhrase))
            if (traverseResult.some(el => el)) {
                node.html.classList.remove('hidden')
                return true
            } else {
                node.html.classList.add('hidden')
                return false
            }
        }
        else {
            node.html.classList.add('hidden')
            return false
        }
    }
}