/** @type {import('./$types').PageLoad} */
export async function load() {
	const response = await fetch('http://127.0.0.1:5000/');

	const articles = await response.json();

	return {
		articles
	};
}
