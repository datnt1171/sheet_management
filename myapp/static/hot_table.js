function mergeCells() {
    const data = hot.getData();
    const mergeRanges = [];

    function findMergeRange(startRow, col) {
        let row = startRow;
        while (row < data.length - 1 && (data[row + 1][0] === null || data[row + 1][0] === '')) { 
            row++;
        }
        if (row > startRow) {
            return { row: startRow, col: col, rowspan: row - startRow + 1, colspan: 1 };
        }
        return null;
    }

    for (let row = 0; row < data.length; row++) {
        if (data[row][0] !== null && data[row][0] !== '') { 
            for (let col = 0; col <= 8; col++) { 
                let mergeRange = findMergeRange(row, col);
                if (mergeRange) {
                    mergeRanges.push(mergeRange);
                }
            }
            row += mergeRanges.length > 0 ? mergeRanges[mergeRanges.length - 1].rowspan - 1 : 0;
        }
    }

    hot.updateSettings({ mergeCells: mergeRanges });
}

function toggleRowIndex() {
    hot.updateSettings({ rowHeaders: hot.getSettings().rowHeaders ? false : true });
}

function exportToExcel() {
    const data = hot.getData();
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(data);

    // Apply merged cells
    const mergeRanges = hot.getPlugin('mergeCells').mergedCellsCollection.mergedCells;
    ws['!merges'] = mergeRanges.map(range => ({
        s: { r: range.row, c: range.col },
        e: { r: range.row + range.rowspan - 1, c: range.col + range.colspan - 1 }
    }));

    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
    XLSX.writeFile(wb, 'table.xlsx');
}