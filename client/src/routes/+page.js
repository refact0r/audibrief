import { PUBLIC_API_URL } from '$env/static/public';

/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
	console.log('API_URL', PUBLIC_API_URL);

	const response = await fetch(PUBLIC_API_URL + 'test');

	const articles = await response.json();

	return {
		articles
	};
}
