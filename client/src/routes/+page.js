import { PUBLIC_API_URL } from '$env/static/public';
import example from '$lib/example.json';

/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
	console.log('API_URL', PUBLIC_API_URL);

	// fetch data from the server
	// const response = await fetch(PUBLIC_API_URL);

	// async function readAllChunks(readableStream) {
	// 	const reader = readableStream.getReader();
	// 	const chunks = [];

	// 	let done, value;
	// 	while (!done) {
	// 		({ value, done } = await reader.read());
	// 		if (done) {
	// 			return chunks;
	// 		}
	// 		chunks.push(value);
	// 	}
	// }

	// let allchunks = await readAllChunks(response.body);

	// let string = '';
	// for (let chunk of allchunks) {
	// 	string += new TextDecoder().decode(chunk);
	// }

	// let articles = JSON.parse(string);

	return {
		articles: example
	};
}
