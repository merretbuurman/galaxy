import { fetcher } from "@/schema";

import { CollectionEntry, DatasetCollectionAttributes, DCESummary, HDCADetailed, isHDCA } from ".";

const DEFAULT_LIMIT = 50;

const getCollectionDetails = fetcher.path("/api/dataset_collections/{id}").method("get").create();

export async function fetchCollectionDetails(params: { hdcaId: string }): Promise<HDCADetailed> {
    const { data } = await getCollectionDetails({ id: params.hdcaId });
    return data;
}

const getCollectionContents = fetcher
    .path("/api/dataset_collections/{hdca_id}/contents/{parent_id}")
    .method("get")
    .create();

export async function fetchCollectionElements(params: {
    /** The ID of the top level HDCA that associates this collection with the History it belongs to. */
    hdcaId: string;
    /** The ID of the collection itself. */
    collectionId: string;
    /** The offset to start fetching elements from. */
    offset?: number;
    /** The maximum number of elements to fetch. */
    limit?: number;
}): Promise<DCESummary[]> {
    const { data } = await getCollectionContents({
        instance_type: "history",
        hdca_id: params.hdcaId,
        parent_id: params.collectionId,
        offset: params.offset,
        limit: params.limit,
    });
    return data;
}

export async function fetchElementsFromCollection(params: {
    /** The HDCA or sub-collection to fetch elements from. */
    entry: CollectionEntry;
    /** The offset to start fetching elements from. */
    offset?: number;
    /** The maximum number of elements to fetch. */
    limit?: number;
}): Promise<DCESummary[]> {
    const hdcaId = isHDCA(params.entry) ? params.entry.id : params.entry.hdca_id;
    const collectionId = isHDCA(params.entry) ? params.entry.collection_id : params.entry.id;
    return fetchCollectionElements({
        hdcaId: hdcaId,
        collectionId: collectionId,
        offset: params.offset ?? 0,
        limit: params.limit ?? DEFAULT_LIMIT,
    });
}

const getCollectionAttributes = fetcher.path("/api/dataset_collections/{id}/attributes").method("get").create();

export async function fetchCollectionAttributes(params: { hdcaId: string }): Promise<DatasetCollectionAttributes> {
    const { data } = await getCollectionAttributes({ id: params.hdcaId, instance_type: "history" });
    return data;
}
