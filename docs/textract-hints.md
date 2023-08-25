# Textract installation hints

Textract needs [Poppler](https://poppler.freedesktop.org/) to extract text from PDFs.

## Windows

1. Download the latest binary of your choice from [github.com/oschwartz10612](https://github.com/oschwartz10612/poppler-windows/releases). In this example we will download and use [Release-22.01.0-0.zip](https://github.com/oschwartz10612/poppler-windows/releases/download/v22.01.0-0/Release-22.01.0-0.zip).
2. Extract the archive file _Release-22.01.0-0.zip_
3. Copy the folders from _poppler-22.01.0\Library_ into `C:\Program Files\Poppler`.
4. Thus, the directory structure should look something like this:

```
C:\Program Files\Poppler
                        \bin
                        \include
                        \lib
                        \share
```

5. Add `C:\Program Files\Poppler\bin` to your system PATH!
6. Try it with a [filecontent example rule](https://organize.readthedocs.io/en/latest/filters/#filecontent)
