package com.phonecluster.app.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Upload
import androidx.compose.material.icons.filled.CloudUpload
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.phonecluster.app.utils.FileChunker
import com.phonecluster.app.utils.FileChunk
import com.phonecluster.app.utils.ChunkedFileInfo
import com.phonecluster.app.utils.ChunkUploader
import com.phonecluster.app.storage.PreferencesManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UserModeScreen(onBackClick: () -> Unit = {}) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    // State variables
    var selectedFileUri by remember { mutableStateOf<Uri?>(null) }
    var fileInfo by remember { mutableStateOf<ChunkedFileInfo?>(null) }
    var chunks by remember { mutableStateOf<List<FileChunk>>(emptyList()) }
    var isChunking by remember { mutableStateOf(false) }
    var chunkingProgress by remember { mutableStateOf(0 to 0) } // (current, total)
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Upload state
    var isUploading by remember { mutableStateOf(false) }
    var uploadProgress by remember { mutableStateOf(0 to 0) } // (uploaded, total)
    var uploadedFileId by remember { mutableStateOf<Int?>(null) }

    // File picker launcher
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            selectedFileUri = it
            fileInfo = FileChunker.getFileInfo(context, it)
            chunks = emptyList() // Reset chunks when new file selected
            errorMessage = null
            uploadedFileId = null
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("User Mode") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Header
                Text(
                    text = "File Upload & Management",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                // File Picker Button
                ElevatedButton(
                    onClick = { filePickerLauncher.launch("*/*") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp)
                ) {
                    Icon(Icons.Default.Upload, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Select File")
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Error Message
                errorMessage?.let { error ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = error,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }

                // Success Message
                uploadedFileId?.let { id ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.tertiaryContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = "✅ File uploaded successfully!\nFile ID: $id",
                            color = MaterialTheme.colorScheme.onTertiaryContainer,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }

                // File Info Card
                fileInfo?.let { info ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.primaryContainer
                        )
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.Description,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "File Information",
                                    style = MaterialTheme.typography.titleMedium,
                                    color = MaterialTheme.colorScheme.onPrimaryContainer
                                )
                            }

                            Spacer(modifier = Modifier.height(12.dp))

                            InfoRow("Name:", info.name)
                            InfoRow("Size:", FileChunker.formatFileSize(info.size))
                            InfoRow("Type:", info.mimeType ?: "Unknown")
                            InfoRow("Total Chunks:", "${info.totalChunks} (10KB each)")
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Chunk Button
                    Button(
                        onClick = {
                            scope.launch {
                                isChunking = true
                                errorMessage = null

                                try {
                                    chunks = withContext(Dispatchers.IO) {
                                        FileChunker.chunkFile(
                                            context,
                                            selectedFileUri!!
                                        ) { current, total ->
                                            chunkingProgress = current to total
                                        }
                                    }
                                } catch (e: Exception) {
                                    errorMessage = "Chunking failed: ${e.message}"
                                    e.printStackTrace()
                                } finally {
                                    isChunking = false
                                }
                            }
                        },
                        enabled = !isChunking && chunks.isEmpty(),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp)
                    ) {
                        Text(if (isChunking) "Chunking..." else "Chunk File")
                    }

                    // Chunking Progress
                    if (isChunking) {
                        Spacer(modifier = Modifier.height(8.dp))
                        LinearProgressIndicator(
                            modifier = Modifier.fillMaxWidth()
                        )
                        Text(
                            text = "Processing chunk ${chunkingProgress.first}...",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }

                    // Upload Button (only show when chunks are ready)
                    if (chunks.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(12.dp))

                        Button(
                            onClick = {
                                scope.launch {
                                    isUploading = true
                                    errorMessage = null
                                    uploadedFileId = null
                                    uploadProgress = 0 to chunks.size

                                    try {
                                        // IMPORTANT: Change this to your PC's IP address
                                        val baseUrl = "http://192.168.1.8:8000"

                                        val userId = 1 // TODO: Get from actual user session

                                        val fileId = withContext(Dispatchers.IO) {
                                            ChunkUploader.uploadAll(
                                                baseUrl = baseUrl,
                                                userId = userId,
                                                fileInfo = info,
                                                chunks = chunks
                                            ) { uploaded, total ->
                                                uploadProgress = uploaded to total
                                            }
                                        }

                                        uploadedFileId = fileId
                                    } catch (e: Exception) {
                                        errorMessage = "Upload failed: ${e.message}"
                                        e.printStackTrace()
                                    } finally {
                                        isUploading = false
                                    }
                                }
                            },
                            enabled = !isUploading,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(48.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.tertiary
                            )
                        ) {
                            Icon(Icons.Default.CloudUpload, contentDescription = null)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(if (isUploading) "Uploading..." else "Upload to Server")
                        }

                        // Upload Progress
                        if (isUploading) {
                            Spacer(modifier = Modifier.height(8.dp))
                            LinearProgressIndicator(
                                progress = uploadProgress.first.toFloat() / uploadProgress.second.toFloat(),
                                modifier = Modifier.fillMaxWidth()
                            )
                            Text(
                                text = "Uploaded ${uploadProgress.first}/${uploadProgress.second} chunks",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Chunks List
                if (chunks.isNotEmpty()) {
                    Text(
                        text = "Chunks (${chunks.size})",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.align(Alignment.Start)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    LazyColumn(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(chunks) { chunk ->
                            ChunkCard(chunk)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
            modifier = Modifier.width(100.dp)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onPrimaryContainer
        )
    }
}

@Composable
private fun ChunkCard(chunk: FileChunk) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Chunk #${chunk.index}",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
                Text(
                    text = FileChunker.formatFileSize(chunk.size.toLong()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
            }

            Surface(
                shape = MaterialTheme.shapes.small,
                color = MaterialTheme.colorScheme.primary
            ) {
                Text(
                    text = "Ready",
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                    color = MaterialTheme.colorScheme.onPrimary,
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }
    }
}