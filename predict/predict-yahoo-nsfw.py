## NOTE: Must install caffe. Use `brew install caffe`

import PIL.Image as Image

from nsfw import classify

image = Image.open("/Users/nathanmurray/Downloads/16156.md.jpg")
sfw, nsfw = classify(image)

print("SFW Probability: {}".format(sfw))
print("NSFW Probability: {}".format(nsfw))