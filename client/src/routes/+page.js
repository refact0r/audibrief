import { PUBLIC_API_URL } from '$env/static/public';

/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
	console.log('API_URL', PUBLIC_API_URL);

	// fetch data from the server
	const response = await fetch(PUBLIC_API_URL + 'test');

	// parse the response as JSON
	const articles = await response.json();

	return {
		articles
	};
}
