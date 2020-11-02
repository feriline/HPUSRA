chrome.browserAction.setBadgeText({text: "ON"});
chrome.browserAction.setBadgeBackgroundColor({color: '#32cd32'});
chrome.browserAction.onClicked.addListener(function () {
    chrome.browserAction.getBadgeText({}, function (result) {
//         if (window.File && window.FileReader && window.FileList && window.Blob) {
//             console.log('Great success! All the File APIs are supported.');
//             // ###################################################################
//             function onQuotaRequestSuccess(grantedQuota) {
//
//                 function saveFile(directoryEntry) {
//                     console.log('FS name: ' + directoryEntry.name);
//                     function createFileWriter(fileEntry) {
//
//                         function write(fileWriter) {
//                             var dataBlob = new Blob(["Hello world!"], {type: "text/plain"});
//                             fileWriter.write(dataBlob);
//                         }
//
//                         fileEntry.createWriter(write);
//                     }
//
//                     directoryEntry.getFile(
//                         "testFile",
//                         {create: true, exclusive: true},
//                         createFileWriter
//                     );
//                 }
//
//                 window.requestFileSystem = window.requestFileSystem || window.webkitRequestFileSystem;
//                 window.requestFileSystem(Window.PERSISTENT, grantedQuota, saveFile, function (e) {
//                         var msg = '';
//
//                         switch (e.code) {
//                             case FileError.QUOTA_EXCEEDED_ERR:
//                                 msg = 'QUOTA_EXCEEDED_ERR';
//                                 break;
//                             case FileError.NOT_FOUND_ERR:
//                                 msg = 'NOT_FOUND_ERR';
//                                 break;
//                             case FileError.SECURITY_ERR:
//                                 msg = 'SECURITY_ERR';
//                                 break;
//                             case FileError.INVALID_MODIFICATION_ERR:
//                                 msg = 'INVALID_MODIFICATION_ERR';
//                                 break;
//                             case FileError.INVALID_STATE_ERR:
//                                 msg = 'INVALID_STATE_ERR';
//                                 break;
//                             default:
//                                 msg = 'Unknown Error';
//                                 break;
//                         }
//                         console.log('Error: ' + msg);
//                     }
//                 );
//             }
//
//             var desiredQuota = 5 * 1024 * 1024;
//             // var quotaManagementObj = navigator.webkitPersistentStorage;
//             // quotaManagementObj.requestQuota(desiredQuota, onQuotaRequestSuccess);
//             // window.webkitStorageInfo.requestQuota(PERSISTENT, desiredQuota, onQuotaRequestSuccess, function (e) {
//             //     console.log('Error: ', e);
//             // });
//             navigator.webkitPersistentStorage.requestQuota(desiredQuota, onQuotaRequestSuccess, function (e) {
//                 console.log('Error: ', e);
//             });
//
// // ###################################################################
// // var d = new Date(2013, 12, 5, 16, 23, 45, 600);
// // var generatedFile = new File(["Rough Draft ...."], "c:\\Draft1.txt", {type: "text/plain", lastModified: d});
// // generatedFile.write('testing string.')
// // ###################################################################
//         } else {
//             console.log('The File APIs are not fully supported in this browser.');
//         }
//


        // // ****************************************************************
        // var ExcelApp = new ActiveXObject("Excel.Application");
        // var ExcelSheet = new ActiveXObject("Excel.Sheet");
        // // Make Excel visible through the Application object.
        // ExcelSheet.Application.Visible = true;
        // // Place some text in the first cell of the sheet.
        // ExcelSheet.ActiveSheet.Cells(1, 1).Value = "This is column A, row 1";
        // // Save the sheet.
        // ExcelSheet.SaveAs("C:\\TEST.XLS");
        // // Close Excel with the Quit method on the Application object.
        // ExcelSheet.Application.Quit();
        // // ****************************************************************

        if (result == "ON") {
            chrome.browserAction.setBadgeText({text: "OFF"});
            chrome.browserAction.setBadgeBackgroundColor({color: '#ff0000'});
            console.log('Turned off. ' + new Date().toString());
        }
        else {
            chrome.browserAction.setBadgeText({text: "ON"});
            chrome.browserAction.setBadgeBackgroundColor({color: '#32cd32'});
            console.log('Turned on. ' + new Date().toString());
        }
    })
    ;
})
;

// ********************************************************************
chrome.tabs.onUpdated.addListener(checkForValidUrl);
function checkForValidUrl(tabId, changeInfo, tab) {
    // if (tab.url.indexOf('https') > -1) {
    chrome.browserAction.getBadgeText({}, function (result) {
        if (result == "ON") {
            console.log("\n<Time>" + new Date().toString() + "</Time><Browser>Chrome</Browser><URL>" + tab.url + "</URL>\n");
        }
    });
    // window.requestFileSystem(window.PERSISTENT, 5 * 1024 * 1024, initFs);
    //
    // function initFs(fs) {
    //     fs.root.getFile
    //     ('log.txt', {create: true, exclusive: true}, function (fileEntry) {
    //         fileEntry.isFile = true;
    //         fileEntry.name = 'log.txt';
    //         fileEntry.fullPath = '/log.txt';
    //         fileEntry.createWriter(function (fileWriter) {
    //             fileWriter.seek(fileWriter.length);
    //             var bb = new BlobBuilder();
    //             bb.append("\n<TimeStamp>" + getTimestamp() + "</TimeStamp><Browser>Chrome</Browser><URL>" + tabURL + "</URL>\n");
    //             fileWriter.write(bb.getBlob('text/plain'));
    //         });
    //     });
    // }
    // }
}

// ********************************************************************
// var sites = [];
//
// function startAction() {
//     chrome.tabs.getSelected(null, function (tab) {
//         var tablink = tab.url;
//         var len = sites.length;
//         for (var i = 0; i < len; i++) {
//             if (sites[i] == tablink) {
//                 console.log("Already in list");
//             }
//         }
//         if (i == len) {
//             sites[i] = tablink;
//             console.log("Newly added");
//         }
//     });
//     print();
// }
//
// function print() {
//     var len = sites.length;
//     for (var i = 0; i < len; i++) {
//         console.log(sites[i]);
//     }
// }
//
// startAction();