var mix = {
	methods: {
		signUp () {
			const uname = 'Tom'
//			const uname = document.querySelector('#uname').value
			const username = document.querySelector('#login').value
			const password = document.querySelector('#password').value
//			this.postData('/api/sign-up/', JSON.stringify({ uname, username, password }))
			this.postData('/api/sign-up/', JSON.stringify({ password }))
				.then(({ data, status }) => {
					location.assign(`/`)
				})
		}
	},
	mounted() {
	},
	data() {
		return {}
	}
}